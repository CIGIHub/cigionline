from django.core.management.base import BaseCommand
from django.db.models import Count

from people.models import PersonPage, PersonType

# BugHerd #335 (Juode 9/4, Tia 9/10): a person page with no bio and no contact
# details is a blank landing — archive those pages instead of showing them.
# "Archive" here = the site's archive flag (drops the page out of every people
# listing/router, which all filter archive=0) AND unpublish (the URL stops
# resolving, so a reader can't land on the blank page from a stale link).
# Dry-run by default; --apply writes and records a reversal CSV (page ids).


class Command(BaseCommand):
    help = (
        'Archive + unpublish live PersonPages that carry no bio and no contact '
        'details (BugHerd #335). Dry-run by default — pass --apply to write.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Execute writes (default: dry-run).')
        parser.add_argument('--reversal-csv', default='archive_empty_people-reversal.csv',
                            help='Where to record the affected page ids (apply only).')
        parser.add_argument(
            '--include-authors', action='store_true',
            help='Also archive people credited as an author on live content. Default: skip '
                 'them — their bylines link to the person page, and unpublishing it would '
                 'break every byline link (most are External profile guest authors).')

    def queryset(self, include_authors=False):
        qs = (PersonPage.objects.live()
              .filter(archive=0, short_bio='', email='', phone_number='',
                      linkedin_url='', twitter_username=''))
        if not include_authors:
            qs = qs.filter(content_pages_as_author__isnull=True)
        return qs.distinct().order_by('last_name', 'first_name')

    def handle(self, *args, **options):
        pages = self.queryset(options['include_authors'])
        total = pages.count()
        skipped_authors = 0
        if not options['include_authors']:
            skipped_authors = (self.queryset(True).filter(content_pages_as_author__isnull=False)
                               .distinct().count())
        if not total:
            self.stdout.write('No live, unarchived people without bio + contact details — nothing to do.')
            return

        by_type = (PersonType.objects.filter(personpage__in=pages)
                   .annotate(n=Count('personpage')).order_by('-n').values_list('name', 'n'))
        self.stdout.write(f'{total} live people carry no bio and no contact details.')
        for name, n in by_type:
            self.stdout.write(f'  {n:5d}  {name}')
        untyped = pages.filter(person_types__isnull=True).count()
        if untyped:
            self.stdout.write(f'  {untyped:5d}  (no person type)')
        if options['include_authors']:
            authored = pages.filter(content_pages_as_author__isnull=False).distinct().count()
            self.stdout.write(f'  {authored} of them are credited as an author on live content.')
        elif skipped_authors:
            self.stdout.write(f'  Skipped {skipped_authors} more who are credited authors on live '
                              f'content (pass --include-authors to archive them too).')
        self.stdout.write('')
        for page in pages.only('id', 'slug', 'title'):
            self.stdout.write(f'archive   {page.id}  {page.slug}')

        if not options['apply']:
            self.stdout.write('\nDry run — nothing written. Re-run with --apply to archive + unpublish.')
            return

        import csv
        ids = list(pages.values_list('id', flat=True))
        with open(options['reversal_csv'], 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['page_id'])
            w.writerows([[i] for i in ids])
        for page in PersonPage.objects.filter(id__in=ids):
            page.archive = PersonPage.ArchiveStatus.ARCHIVED
            page.save(update_fields=['archive'])
            page.unpublish(set_expired=False, log_action=True)
        self.stdout.write(f'\nArchived + unpublished {len(ids)} pages. Reversal ids: {options["reversal_csv"]}')
