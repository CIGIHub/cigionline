"""Shape catalogue for visual QA of the redesigned page types.

Every converted page is reduced to a *render signature* — the set of body
block types plus the presentation-relevant page fields that change what the
template draws (hero banner vs image, authors, series membership, footnotes,
supporting materials, embeds, …). Pages sharing a signature render the same
"shape", so QA'ing one example covers the whole group.

Output (docs/redesign/shape-catalogue.md) lists, per page type, one row per
distinct signature ordered by page count descending: count · a staging link to
the most-recently-published example · the signature. Start at the top row
(thousands of pages) and work into the long tail of one-off shapes.

    python manage.py shape_catalogue --report docs/redesign/shape-catalogue.md
    python manage.py shape_catalogue --type articles.ArticlePage

Regenerate whenever content shifts materially — same idea as the block census.
"""
from collections import defaultdict
from datetime import datetime, timezone

from django.core.management.base import BaseCommand, CommandError

STAGING = 'https://cigionline-staging-takt-f3749410f2fd.herokuapp.com'


def _blocks(page):
    body = getattr(page, 'body', None)
    if body is None:
        return frozenset()
    try:
        return frozenset(b['type'] for b in body.raw_data)
    except Exception:  # noqa: BLE001 — non-stream or unparseable body
        return frozenset()


def _stream_has(page, attr):
    """True when a StreamField/related attr holds at least one item."""
    val = getattr(page, attr, None)
    try:
        return bool(val) and len(val) > 0
    except TypeError:
        return bool(val)


def _article_type(page):
    at = getattr(page, 'article_type', None)
    return getattr(at, 'title', '') if at else ''


# Presentation-relevant field flags per type. Each is (name, predicate); a flag
# whose predicate is true joins the signature. Kept to fields the single-page
# templates actually branch on (see article_page/publication_page/etc.).
FLAG_SPECS = {
    'articles.ArticlePage': [
        ('banner', lambda p: bool(p.image_banner_id)),
        ('hero-img', lambda p: bool(p.image_hero_id) and not p.image_banner_id),
        ('subtitle', lambda p: bool(p.subtitle)),
        ('authors', lambda p: p.author_count > 0),
        ('multi-author', lambda p: p.author_count > 1),
        ('series-intro', lambda p: bool(getattr(p, 'article_series_description', ''))),
        ('opinion-series', lambda p: bool(getattr(p, 'opinion_series_description', ''))),
        ('from-archives', lambda p: bool(p.from_the_archives and p.from_the_archives_blurb)),
        ('footnotes', lambda p: bool(p.footnotes)),
        ('works-cited', lambda p: bool(p.works_cited)),
        ('supporting', lambda p: _stream_has(p, 'related_files')),
        ('news-excerpt', lambda p: _article_type(p) in ('CIGI in the News', 'News Releases')),
    ],
    'publications.PublicationPage': [
        ('book', lambda p: getattr(getattr(p, 'publication_type', None), 'title', '') == 'Books'),
        ('banner', lambda p: bool(p.image_banner_id)),
        ('hero-img', lambda p: bool(p.image_hero_id) and not p.image_banner_id),
        ('subtitle', lambda p: bool(p.subtitle)),
        ('authors', lambda p: p.author_count > 0),
        ('editors', lambda p: getattr(p, 'editor_count', 0) > 0),
        ('series', lambda p: bool(p.publication_series_id)),
        ('issuu', lambda p: bool(getattr(p, 'embed_issuu', ''))),
        ('excerpt-dl', lambda p: bool(getattr(p, 'book_excerpt_download_id', None))),
        ('isbn', lambda p: bool(getattr(p, 'isbn', ''))),
        ('pdfs', lambda p: _stream_has(p, 'pdf_downloads')),
        ('from-archives', lambda p: bool(p.from_the_archives and p.from_the_archives_blurb)),
    ],
    'events.EventPage': [
        ('banner', lambda p: bool(p.image_banner_id)),
        ('hero-img', lambda p: bool(p.image_hero_id) and not p.image_banner_id),
        ('subtitle', lambda p: bool(p.subtitle)),
        ('authors', lambda p: p.author_count > 0),
        ('past-video', lambda p: bool(p.multimedia_page_id)),
        ('agenda', lambda p: _stream_has(p, 'event_agenda')),
        ('supporting', lambda p: _stream_has(p, 'related_files')),
    ],
    'multimedia.MultimediaPage': [
        ('audio', lambda p: getattr(p, 'multimedia_type', '') == 'audio'),
        ('video', lambda p: getattr(p, 'multimedia_type', '') == 'video'),
        ('banner', lambda p: bool(p.image_banner_id)),
        ('hero-img', lambda p: bool(p.image_hero_id) and not p.image_banner_id),
        ('subtitle', lambda p: bool(p.subtitle)),
        ('authors', lambda p: p.author_count > 0),
        ('series', lambda p: bool(p.multimedia_series_id)),
        ('guests', lambda p: _stream_has(p, 'podcast_guests')),
        ('series-intro', lambda p: bool(getattr(p, 'article_series_description', ''))),
        ('from-archives', lambda p: bool(p.from_the_archives and p.from_the_archives_blurb)),
    ],
    'people.PersonPage': [
        ('position', lambda p: bool(getattr(p, 'position', ''))),
        ('expertise', lambda p: _stream_has(p, 'expertise')),
        ('topics', lambda p: p.topics.exists()),
        ('projects', lambda p: p.projects.exists()),
        ('person-types', lambda p: p.person_types.exists()),
    ],
    'core.BasicPage': [
        ('banner', lambda p: bool(p.image_banner_id)),
        ('hero-img', lambda p: bool(p.image_hero_id) and not p.image_banner_id),
        ('subtitle', lambda p: bool(p.subtitle)),
    ],
    'research.ProjectPage': [],   # body block-type set carries the shape
}

# app_label.ModelName -> import path
TYPES = {
    'articles.ArticlePage': ('articles.models', 'ArticlePage'),
    'publications.PublicationPage': ('publications.models', 'PublicationPage'),
    'events.EventPage': ('events.models', 'EventPage'),
    'multimedia.MultimediaPage': ('multimedia.models', 'MultimediaPage'),
    'people.PersonPage': ('people.models', 'PersonPage'),
    'core.BasicPage': ('core.models', 'BasicPage'),
    'research.ProjectPage': ('research.models', 'ProjectPage'),
}

_MIN_DT = datetime.min.replace(tzinfo=timezone.utc)


def _recency(page):
    for attr in ('publishing_date', 'first_published_at', 'latest_revision_created_at'):
        val = getattr(page, attr, None)
        if val:
            return val if getattr(val, 'tzinfo', None) else \
                datetime(val.year, val.month, val.day, tzinfo=timezone.utc)
    return _MIN_DT


class Command(BaseCommand):
    help = ('Catalogue distinct render signatures (block types + presentation '
            'fields) per converted page type, with a staging example each.')

    def add_arguments(self, parser):
        parser.add_argument('--type', help='Only one type, app_label.ModelName.')
        parser.add_argument('--report', help='Write markdown here (also prints).')

    def handle(self, *args, **options):
        wanted = TYPES
        if options['type']:
            if options['type'] not in TYPES:
                raise CommandError(
                    f"{options['type']} not catalogued. Known: {', '.join(TYPES)}")
            wanted = {options['type']: TYPES[options['type']]}

        lines = ['# Shape catalogue — redesigned-page QA',
                 '',
                 'One row per distinct render signature (body block types + '
                 'presentation fields), by page count descending. QA the linked '
                 'example to cover every page in that row. Links point at '
                 'staging.', '']
        grand = 0

        for label, (module, cls_name) in wanted.items():
            mod = __import__(module, fromlist=[cls_name])
            model = getattr(mod, cls_name)
            flags = FLAG_SPECS.get(label, [])
            groups = defaultdict(lambda: {'count': 0, 'example': None, 'rk': _MIN_DT})

            qs = model.objects.live().public()
            for page in qs.iterator(chunk_size=300):
                sig_flags = frozenset(
                    name for name, pred in flags if _safe(pred, page))
                sig = (sig_flags, _blocks(page))
                g = groups[sig]
                g['count'] += 1
                rk = _recency(page)
                if rk >= g['rk']:
                    g['rk'] = rk
                    g['example'] = page

            total = sum(g['count'] for g in groups.values())
            grand += total
            lines.append(f'## {cls_name} — {total} pages, {len(groups)} shapes')
            lines.append('')
            lines.append('| # | Pages | Example (staging) | Fields | Body blocks |')
            lines.append('|---|---:|---|---|---|')
            ranked = sorted(groups.items(),
                            key=lambda kv: kv[1]['count'], reverse=True)
            for i, ((sig_flags, blocks), g) in enumerate(ranked, 1):
                page = g['example']
                parts = page.get_url_parts()
                path = parts[2] if parts else ''
                link = f'[{page.pk}]({STAGING}{path})' if path else str(page.pk)
                fields = ', '.join(sorted(sig_flags)) or '—'
                blk = ', '.join(sorted(blocks)) or '—'
                lines.append(f'| {i} | {g["count"]} | {link} | {fields} | {blk} |')
            lines.append('')
            self.stdout.write(f'{cls_name}: {total} pages → {len(groups)} shapes')
            self.stdout.flush()

        lines.insert(4, f'Total: {grand} pages across {len(wanted)} types.\n')
        report = '\n'.join(lines)
        if options['report']:
            with open(options['report'], 'w') as fh:
                fh.write(report + '\n')
            self.stdout.write(f"\nReport written to {options['report']}")
        else:
            self.stdout.write(report)


def _safe(pred, page):
    try:
        return bool(pred(page))
    except Exception:  # noqa: BLE001 — a missing relation shouldn't abort the sweep
        return False
