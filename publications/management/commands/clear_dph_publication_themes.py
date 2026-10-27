from django.core.management.base import BaseCommand

from publications.models import PublicationPage

# DPH publication cutover (docs/redesign/close-out.md B.12, adjudicated: clear
# as done for the hub pages). The legacy `theme=DPH` FK forces the
# themes/dph/publication_page.html fork via get_template; clearing it flips
# the page to the DS publication single, which applies the green DPH brand
# surface itself off publication_type == Working Paper — no content change.
THEME_NAME = 'DPH'


class Command(BaseCommand):
    help = (
        'Clear the legacy theme FK on DPH-themed PublicationPages so they '
        'render the DS publication single. Idempotent; dry-run by default — '
        'pass --apply to write.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Execute writes (default: dry-run).')

    def handle(self, *args, **options):
        pages = PublicationPage.objects.filter(theme__name=THEME_NAME).order_by('id')
        count = pages.count()
        if not count:
            self.stdout.write(f'No PublicationPages with theme={THEME_NAME} — nothing to do.')
            return

        for page in pages.select_related('publication_type').only(
                'id', 'slug', 'live', 'publication_type'):
            note = ''
            # The DS single derives the green surface from the Working Paper
            # type, not the theme — anything else loses the DPH branding.
            if not (page.publication_type and page.publication_type.slug == 'working-paper'):
                note = '  [WARN: not a working-paper — will render unbranded]'
            status = 'live ' if page.live else 'draft'
            self.stdout.write(f'clear     {page.id}  {status}  {page.slug}{note}')

        if options['apply']:
            updated = pages.update(theme=None)
            self.stdout.write(self.style.SUCCESS(f'Cleared theme on {updated} publication pages.'))
        else:
            self.stdout.write(self.style.WARNING(
                f'Dry run — {count} pages would be cleared; pass --apply to write.'))
