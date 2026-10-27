"""Render-sweep QA: request every live public page through the test client and
classify what it rendered. Total coverage for the class of bug where one field
or block permutation crashes a template (e.g. the resource-carousel accent
lookup that 500'd podcast singles) — run before a staging deploy.

Beyond HTTP status, each 200 is checked for DS markup: the DS chrome
(``ds-header``) and at least one DS *content* module (reading shell, hero,
faceted-listing router, card, carousel, …). A page that returns 200 with chrome
but no content module ('chrome-only') is the actionable QA signal — the shell
loaded but the main body rendered nothing recognisably converted.

Media is stubbed by default (``--real-media`` to disable): image reads return a
tiny in-memory PNG so rendition generation never touches the staging S3 bucket.
This is what makes a full-site sweep finish in minutes instead of hours — the
sweep hunts template/data crashes, which don't need real image bytes.

    python manage.py render_sweep --report docs/redesign/render-sweep.md
    python manage.py render_sweep --type articles.ArticlePage --limit 50
"""
import io
import time
import traceback
from collections import Counter, defaultdict
from urllib.parse import urlparse

from django.core.files.base import ContentFile
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.test import Client

from wagtail.models import Page

# DS chrome — present on every page that extends the DS base.
CHROME_MARKER = 'ds-header'

# DS content modules — substrings that only appear when a converted module or
# shell actually rendered inside <main> (not chrome/footer). Any one present =
# the page rendered real DS content.
CONTENT_MARKERS = (
    'ds-reading',          # reading shell (article/publication/event/multimedia/basic singles)
    'ds-hero',             # any DS hero
    'ds-router',           # faceted-listing controls
    'ds-faceted-listing',
    'ds-prose',            # prose body
    'ds-card',             # shared card (grids, rails)
    'ds-carousel',         # carousels / rails
    'ds-expert-card',
    'ds-composable-tabs',
    'ds-tabs',
    'ds-stat',
    'ds-accordion',
    'ds-module-title',
    'ds-bento',
    'ds-program-grid',
    'ds-news-grid',
    'ds-text-columns',
)

CLASSES = ['ds', 'chrome-only', 'legacy', 'redirect', 'error', 'no-route']


class Command(BaseCommand):
    help = (
        'Request every live public page and classify: ds (chrome + a content '
        "module), chrome-only (200, chrome, no content module), legacy (200, no "
        'DS chrome), redirect, error, no-route. Exits non-zero on any error.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            help='Only sweep one page type, app_label.ModelName '
                 '(e.g. articles.ArticlePage).',
        )
        parser.add_argument('--limit', type=int, help='Stop after N pages.')
        parser.add_argument(
            '--report',
            help='Write a markdown report to this path (summary also prints).',
        )
        parser.add_argument(
            '--real-media', action='store_true',
            help='Disable the media stub and pull real images from staging S3 '
                 '(slow; only needed to exercise the image-file path).',
        )

    def handle(self, *args, **options):
        if not options['real_media']:
            self._stub_media()

        pages = Page.objects.live().public().order_by('pk')
        if options['type']:
            app_label, _, model = options['type'].lower().partition('.')
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model)
            except ContentType.DoesNotExist:
                raise CommandError(f"Unknown page type {options['type']}")
            pages = pages.filter(content_type=ct)
        if options['limit']:
            pages = pages[:options['limit']]

        client = Client()
        by_type = defaultdict(Counter)     # type -> class -> count
        problems = defaultdict(list)       # class -> [(type, id, path, detail)]
        started = time.monotonic()
        total = 0

        for page in pages.select_related('content_type').iterator(chunk_size=500):
            total += 1
            type_name = page.content_type.model_class().__name__
            cls, detail = self._classify(client, page)
            by_type[type_name][cls] += 1
            if cls in ('error', 'no-route'):
                problems[cls].append((type_name, page.pk, detail[1], detail[0]))
            elif cls == 'redirect':
                problems['redirect'].append((type_name, page.pk, detail[1], detail[0]))
            elif cls in ('chrome-only', 'legacy'):
                # Keep a few examples per (class, type) to link from the report.
                same = [p for p in problems[cls]
                        if p[0] == type_name]
                if len(same) < 5:
                    problems[cls].append((type_name, page.pk, detail[1], detail[0]))
            if total % 100 == 0:
                self.stdout.write(f'  …{total} pages in '
                                  f'{time.monotonic() - started:.0f}s')
                self.stdout.flush()  # visible when stdout is a file (background runs)

        report = '\n'.join(
            self._summarise(by_type, problems, total, time.monotonic() - started))
        self.stdout.write(report)
        if options['report']:
            with open(options['report'], 'w') as fh:
                fh.write(report + '\n')
            self.stdout.write(f"\nReport written to {options['report']}")

        if problems['error']:
            raise SystemExit(1)

    @staticmethod
    def _stub_media():
        """Media reads return a tiny valid PNG — no S3, no disk pull. Patch only
        the media storage class, never FileSystemStorage itself (that also backs
        staticfiles' manifest, which must stay real text)."""
        from core.dev_storage import StagingPullThroughStorage
        from PIL import Image
        buf = io.BytesIO()
        Image.new('RGB', (32, 32), '#888').save(buf, 'PNG')
        tiny = buf.getvalue()
        StagingPullThroughStorage._open = \
            lambda self, name, mode='rb': ContentFile(tiny, name=name)

    @staticmethod
    def _classify(client, page):
        """Return (class, detail) where detail carries (extra, path) for reports."""
        url_parts = page.get_url_parts()
        if url_parts is None:
            return 'no-route', ('unroutable', page.url_path or '')
        _, root_url, path = url_parts
        host = urlparse(root_url).hostname or 'localhost'
        try:
            response = client.get(path, HTTP_HOST=host)
        except Exception:  # noqa: BLE001 — classify, keep sweeping
            last = traceback.format_exc().strip().splitlines()[-1]
            return 'error', (last[:300], path)
        if response.status_code in (301, 302):
            return 'redirect', (response.headers.get('Location', ''), path)
        if response.status_code != 200:
            return 'error', (f'HTTP {response.status_code}', path)
        html = response.content.decode('utf-8', errors='ignore')
        if CHROME_MARKER not in html:
            return 'legacy', ('no ds-header', path)
        if not any(m in html for m in CONTENT_MARKERS):
            return 'chrome-only', ('no content module', path)
        return 'ds', ('', path)

    @staticmethod
    def _summarise(by_type, problems, total, elapsed):
        lines = [
            '# Render sweep',
            '',
            f'{total} live public pages in {elapsed:.0f}s (media stubbed).',
            '',
            '- **ds** — DS chrome + at least one DS content module (converted).',
            '- **chrome-only** — 200 with chrome but no content module '
            '(shell loaded, main body rendered nothing DS — inspect).',
            '- **legacy** — 200 without DS chrome (unconverted fork).',
            '',
            '| Page type | ' + ' | '.join(CLASSES) + ' |',
            '|---|' + '---:|' * len(CLASSES),
        ]
        totals = Counter()
        for type_name in sorted(by_type):
            counts = by_type[type_name]
            totals.update(counts)
            row = [str(counts.get(c, '') or '') for c in CLASSES]
            lines.append(f'| {type_name} | ' + ' | '.join(row) + ' |')
        lines.append('| **Total** | ' + ' | '.join(
            str(totals.get(c, 0)) for c in CLASSES) + ' |')

        if problems['error']:
            lines.extend(['', f"## Errors ({len(problems['error'])})", '',
                          '| Type | id | Path | Detail |', '|---|---|---|---|'])
            lines.extend(f'| {p[0]} | {p[1]} | `{p[2]}` | {p[3]} |'
                         for p in problems['error'])

        def section(title, key, fmt):
            if not problems[key]:
                return
            lines.extend(['', f'## {title} ({len(problems[key])})', ''])
            lines.extend(fmt(p) for p in problems[key])

        section('Legacy — no DS chrome (≤5/type)', 'legacy',
                lambda p: f'- {p[0]} {p[1]} `{p[2]}`')
        section('Chrome-only — no content module (≤5/type)', 'chrome-only',
                lambda p: f'- {p[0]} {p[1]} `{p[2]}`')
        section('Unroutable', 'no-route',
                lambda p: f'- {p[0]} {p[1]} `{p[2]}`')
        if problems['redirect']:
            lines.extend(['', f"## Redirects ({len(problems['redirect'])})", ''])
            lines.extend(f'- {p[0]} {p[1]} `{p[2]}` → `{p[3]}`'
                         for p in problems['redirect'][:30])
        return lines
