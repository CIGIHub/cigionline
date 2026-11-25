from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

from research.models import ProjectPage


RENAMES = [
    ('Space Governance 4.0', 'Space Governance'),
    (
        'Strengthening Canada’s National Security in a Complex World',
        'National Security and Cybersecurity',
    ),
    ('Legitimate Influence or Unlawful Manipulation?', 'Freedom of Thought'),
    ('Digital Assets in a Deglobalized World', 'Governance of Digital Money and Assets'),
    (
        'Next-Generation Economies: Middle Powers in a Changing World',
        'Next-Generation Economies',
    ),
    ('Global Economic Scenarios', 'Multilateral and Institutional Reform'),
]

SUPERSEDED_SEED = {
    ('Global Economic Scenarios', 'Multilateral and Institutional Reform'): (
        'Multilateral and Institutional Reform (superseded seed)',
        'multilateral-and-institutional-reform-superseded',
    ),
}


class Command(BaseCommand):
    help = 'Rename legacy project pages to their approved program names.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Publish the title changes (default: dry-run).',
        )

    def handle(self, *args, **options):
        changes = []
        seeds_to_preserve = []
        paths_to_repair = []
        errors = []

        for old_title, new_title in RENAMES:
            sources = list(ProjectPage.objects.filter(title=old_title).order_by('pk')[:2])
            if len(sources) > 1:
                errors.append(f'{old_title!r}: multiple source pages found')
                continue

            if not sources:
                destinations = ProjectPage.objects.filter(
                    Q(title=new_title) | Q(draft_title=new_title)
                )
                count = destinations.count()
                if count == 1:
                    self.stdout.write(f'already renamed: {old_title} -> {new_title}')
                    legacy = SUPERSEDED_SEED.get((old_title, new_title))
                    if legacy:
                        legacy_pages = list(ProjectPage.objects.filter(
                            title=legacy[0], slug=legacy[1]
                        ).order_by('pk')[:2])
                        if len(legacy_pages) > 1:
                            errors.append(f'{legacy[0]!r}: multiple preserved pages found')
                        elif legacy_pages:
                            preserved = legacy_pages[0]
                            expected_path = f'{preserved.get_parent().url_path}{preserved.slug}/'
                            if preserved.url_path != expected_path:
                                paths_to_repair.append(preserved)
                elif count == 0:
                    errors.append(f'{old_title!r}: source page not found')
                else:
                    errors.append(f'{new_title!r}: multiple destination pages found')
                continue

            page = sources[0]
            if page.draft_title == new_title:
                self.stdout.write(f'already renamed: {old_title} -> {new_title}')
                continue

            if page.has_unpublished_changes:
                errors.append(f'{old_title!r}: page has unpublished changes')
                continue

            destinations = list(ProjectPage.objects.exclude(pk=page.pk).filter(
                Q(title=new_title) | Q(draft_title=new_title)
            ).order_by('pk')[:2])
            if destinations:
                legacy = SUPERSEDED_SEED.get((old_title, new_title))
                destination = destinations[0]
                if (
                    len(destinations) != 1
                    or not legacy
                    or destination.slug != 'multilateral-and-institutional-reform'
                    or ProjectPage.objects.exclude(pk=destination.pk).filter(slug=legacy[1]).exists()
                ):
                    errors.append(f'{new_title!r}: destination page already exists')
                    continue
                seeds_to_preserve.append((destination, *legacy))

            changes.append((page, new_title))

        if errors:
            raise CommandError('Rename preflight failed:\n- ' + '\n- '.join(errors))

        for page, legacy_title, legacy_slug in seeds_to_preserve:
            self.stdout.write(
                f'preserve seeded page: {page.title} -> {legacy_title} '
                f'(slug: {legacy_slug})'
            )
        for page in paths_to_repair:
            self.stdout.write(f'repair preserved page path: {page.url_path} -> {page.slug}/')
        for page, new_title in changes:
            self.stdout.write(f'rename: {page.title} -> {new_title} (slug unchanged: {page.slug})')

        if not options['apply']:
            self.stdout.write(self.style.WARNING('Dry run — pass --apply to publish changes.'))
            return

        with transaction.atomic():
            for page, legacy_title, legacy_slug in seeds_to_preserve:
                page.title = legacy_title
                page.draft_title = legacy_title
                page.slug = legacy_slug
                page.save(clean=False)
                page.save_revision(log_action=True).publish()
                page.unpublish()
            for page in paths_to_repair:
                page.set_url_path(page.get_parent())
                page.save(clean=False, update_fields=['url_path'])
            for page, new_title in changes:
                page.title = new_title
                page.save_revision(log_action=True).publish()

        self.stdout.write(self.style.SUCCESS(f'Applied {len(changes)} project page renames.'))
