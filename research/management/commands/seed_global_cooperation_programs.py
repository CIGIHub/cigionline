from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from core.models import BasicPage
from research.models import ProjectPage


PROGRAMS = [
    ('Canada-U.S. Relations in the Second Century', 'canada-us-relations-in-the-second-century'),
]


class Command(BaseCommand):
    help = 'Create the approved net-new Canada-U.S. Relations project-page draft.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Create the draft pages (default: dry-run).',
        )

    def handle(self, *args, **options):
        parents = list(BasicPage.objects.filter(url_path='/home/programs/')[:2])
        if len(parents) != 1:
            raise CommandError(
                "Seed preflight failed: expected one BasicPage at '/home/programs/', "
                f'found {len(parents)}'
            )
        parent = parents[0]

        to_create = []
        errors = []
        for title, slug in PROGRAMS:
            titles = [title]
            if title.startswith('Canada-U.S.'):
                titles.append(title.replace('Canada-U.S.', 'Canada-US'))
            matches = list(ProjectPage.objects.filter(
                Q(title__in=titles) | Q(draft_title__in=titles)
            ).order_by('pk')[:2])

            if len(matches) > 1:
                errors.append(f'{title!r}: multiple ProjectPages found')
                continue
            if matches:
                page = matches[0]
                if page.get_parent().pk != parent.pk or page.slug != slug:
                    errors.append(
                        f'{title!r}: existing page is not at {parent.url}{slug}/'
                    )
                else:
                    self.stdout.write(f'exists: {page.title} ({page.url_path})')
                continue
            if parent.get_children().filter(slug=slug).exists():
                errors.append(f'{title!r}: sibling slug {slug!r} is already in use')
                continue
            to_create.append((title, slug))

        if errors:
            raise CommandError('Seed preflight failed:\n- ' + '\n- '.join(errors))

        for title, slug in to_create:
            self.stdout.write(f'create draft: {title} ({parent.url}{slug}/)')

        if not options['apply']:
            self.stdout.write(self.style.WARNING('Dry run — pass --apply to create pages.'))
            return

        with transaction.atomic():
            for title, slug in to_create:
                page = ProjectPage(
                    title=title,
                    draft_title=title,
                    slug=slug,
                    live=False,
                    has_unpublished_changes=True,
                    publishing_date=timezone.now(),
                )
                parent.add_child(instance=page)
                page.save_revision(log_action=True)

        self.stdout.write(self.style.SUCCESS(f'Created {len(to_create)} draft project pages.'))
