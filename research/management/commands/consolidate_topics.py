from urllib.parse import urlparse

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from wagtail.contrib.redirects.models import Redirect

from core.models import ContentPage
from people.models import PersonPage
from research.models import TopicPage

# Topic consolidation to the 17-tag taxonomy.
# Source of truth: docs/redesign/migration-strategy.md §4 (confirmed 2026-06-11).
# Dry-run by default; idempotent (skips work already done).

RENAMES = [
    ('Artificial Intelligence', 'AI'),
    ('Intellectual Property', 'IP'),
    ('Quantum Technology', 'Quantum'),
    ('Transformative Technologies', 'Emerging Technologies'),
]

# (loser, survivor) — survivor titles are post-rename, so renames run first.
MERGES = [
    ('Competition', 'Digital Economy'),
    ('Digital Rights', 'Human Rights'),
    ('Foreign Interference', 'Democracy'),
    ('Freedom of Thought', 'Human Rights'),
    ('G20/G7', 'Multilateral Institutions'),
    ('Gender', 'Human Rights'),
    ('Global Cooperation', 'Multilateral Institutions'),
    ('Space Governance', 'Emerging Technologies'),
    ('Surveillance', 'Privacy'),
]


class Command(BaseCommand):
    help = (
        'Consolidate research topics to the 17-tag taxonomy: 4 renames, 9 merges, '
        'redirects for every moved URL. Dry-run by default; pass --apply to execute.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Execute changes (default: dry-run, no writes).')

    def handle(self, *args, **options):
        self.apply = options['apply']
        self.stdout.write(f"== Topic consolidation ({'APPLY' if self.apply else 'DRY RUN'}) ==")
        self.do_renames()
        self.do_merges()
        if self.apply:
            self.stdout.write('Done. Run `manage.py update_index` to refresh search.')
        else:
            self.stdout.write('Dry run only — re-run with --apply to execute.')

    def add_redirect(self, old_path, target_page):
        if not old_path:
            self.stderr.write(f'  no URL for redirect to {target_page.title} — skipped')
            return
        # page.url is absolute in multi-site setups; redirects store paths
        old_path = Redirect.normalise_path(urlparse(old_path).path)
        Redirect.objects.update_or_create(
            old_path=old_path,
            site=None,
            defaults={'redirect_page': target_page, 'is_permanent': True},
        )

    def do_renames(self):
        for old_title, new_title in RENAMES:
            topic = TopicPage.objects.filter(title=old_title).first()
            if topic is None:
                done = TopicPage.objects.filter(title=new_title).exists()
                self.stdout.write(f"rename: {old_title} -> {new_title}: skip ({'already renamed' if done else 'NOT FOUND'})")
                continue

            new_slug = slugify(new_title)
            if TopicPage.objects.exclude(pk=topic.pk).filter(slug=new_slug).exists():
                self.stderr.write(f'rename: {old_title}: slug "{new_slug}" already taken — skipped, resolve manually')
                continue

            old_path = topic.url
            self.stdout.write(f'rename: {old_title} ({topic.slug}) -> {new_title} ({new_slug}); redirect {old_path}')
            if self.apply:
                topic.title = new_title
                topic.draft_title = new_title
                topic.slug = new_slug
                topic.save()
                self.add_redirect(old_path, topic)

    def remap(self, queryset, loser, survivor):
        count = 0
        for page in queryset:
            if survivor not in page.topics.all():
                page.topics.add(survivor)
            page.topics.remove(loser)
            page.save()
            count += 1
        return count

    def do_merges(self):
        for loser_title, survivor_title in MERGES:
            loser = TopicPage.objects.filter(title=loser_title).first()
            if loser is None:
                self.stdout.write(f'merge: {loser_title}: skip (not found / already merged)')
                continue
            survivor = TopicPage.objects.filter(title=survivor_title).first()
            if survivor is None:
                # survivor titles are post-rename; in dry-run the renames
                # haven't happened, so fall back to the pre-rename title
                pre_rename = {new: old for old, new in RENAMES}.get(survivor_title)
                if pre_rename:
                    survivor = TopicPage.objects.filter(title=pre_rename).first()
            if survivor is None:
                self.stderr.write(f'merge: {loser_title} -> {survivor_title}: SURVIVOR MISSING — skipped')
                continue

            content = ContentPage.objects.filter(topics=loser)
            people = PersonPage.objects.filter(topics=loser)
            self.stdout.write(
                f'merge: {loser_title} -> {survivor_title}: {content.count()} content pages, '
                f'{people.count()} people; archive + redirect {loser.url}'
            )
            if self.apply:
                old_path = loser.url
                self.remap(content, loser, survivor)
                self.remap(people, loser, survivor)
                self.add_redirect(old_path, survivor)
                loser.archive = 1
                loser.save()
                loser.unpublish()
