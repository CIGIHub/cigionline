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
]


class Command(BaseCommand):
    help = 'Rename the five legacy project pages to their approved program names.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Publish the title changes (default: dry-run).',
        )

    def handle(self, *args, **options):
        changes = []
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

            if ProjectPage.objects.exclude(pk=page.pk).filter(
                Q(title=new_title) | Q(draft_title=new_title)
            ).exists():
                errors.append(f'{new_title!r}: destination page already exists')
                continue

            changes.append((page, new_title))

        if errors:
            raise CommandError('Rename preflight failed:\n- ' + '\n- '.join(errors))

        for page, new_title in changes:
            self.stdout.write(f'rename: {page.title} -> {new_title} (slug unchanged: {page.slug})')

        if not options['apply']:
            self.stdout.write(self.style.WARNING('Dry run — pass --apply to publish changes.'))
            return

        with transaction.atomic():
            for page, new_title in changes:
                page.title = new_title
                page.save_revision(log_action=True).publish()

        self.stdout.write(self.style.SUCCESS(f'Applied {len(changes)} project page renames.'))
