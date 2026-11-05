"""Seed the ported listing pages with their default DS module composition.

The Events, Experts and Annual Reports landings used to render a hardcoded
router in their page template. They now compose from the body module library,
so each needs a faceted-listing block in its body to render the directory it
used to hardcode (BugHerd #135). This command writes that default composition:

  - Events (`events.EventListPage`): a Resource Bento over the browse listing.
  - Experts (`people.PersonListPage`, EXPERTS type): the expert directory.
  - Annual Reports (`annual_reports.AnnualReportListPage`): the report listing.
  - Opinions (`articles.ArticleLandingPage`): a Resource Bento replaces the
    retired listing (BugHerd #124).

Each block keeps the facets its retired page router offered, so the rendered
page matches what shipped before — authors reorder or add modules from there.

Dry-run by default — pass --apply to write. --force overwrites a non-empty body.
"""
import logging
from contextlib import contextmanager

from django.core.management.base import BaseCommand


@contextmanager
def _quiet_search_logging():
    """Silence the search-index logger for the duration of a publish (see
    seed_homepage): an unreachable backend logs a full traceback although the
    publish itself succeeds."""
    logger = logging.getLogger('modelsearch')
    previous = logger.level
    logger.setLevel(logging.CRITICAL)
    try:
        yield
    finally:
        logger.setLevel(previous)


def _listing(prefix, card_type, facets, heading='', empty_text=''):
    """One faceted-listing block value mirroring a retired page router."""
    return ('faceted_listing', {
        'surface': 'inherit',
        'accent': '',
        'heading': heading,
        'card_type': card_type,
        'prefix': prefix,
        'show_filters': True,
        'show_search': True,
        'facets': facets,
        'empty_text': empty_text,
    })


class Command(BaseCommand):
    help = 'Seed the Events / Experts / Annual Reports bodies with their listing modules.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Write changes (otherwise dry-run).')
        parser.add_argument('--force', action='store_true', help='Overwrite an existing non-empty body.')

    def handle(self, *args, **options):
        from annual_reports.models import AnnualReportListPage
        from articles.models import ArticleLandingPage
        from events.models import EventListPage
        from people.models import PersonListPage

        apply = options['apply']
        force = options['force']

        targets = []

        # Events: the Resource Bento Tia asked for above the browse listing
        # (BugHerd #135); the listing keeps the retired router's facet set.
        for page in EventListPage.objects.all():
            if page.get_site() and page.get_site().site_name == 'Think 7 Canada':
                continue  # Think 7 keeps its own template + featured_events.
            targets.append((page, [
                ('resource_bento', {
                    'heading': 'Featured Events',
                    'mode': 'manual',
                    'layout': 'split',
                    'items': list(page.get_featured_events()[:5]),
                    'show_header': True,
                    'show_date': True,
                    'show_author': False,
                }),
                _listing('events', 'event',
                         ['topic', 'location', 'type', 'date'],
                         heading='Browse Events',
                         empty_text='No events match your filters.'),
            ]))

        for page in PersonListPage.objects.filter(
                person_list_page_type=PersonListPage.PersonListPageType.EXPERTS):
            targets.append((page, [
                _listing('experts', 'expert', ['type', 'topic'],
                         empty_text='No experts match your filters.'),
            ]))

        for page in AnnualReportListPage.objects.all():
            targets.append((page, [
                _listing('reports', 'report', ['year'],
                         empty_text='No annual reports match your filters.'),
            ]))

        # Opinions landing (BugHerd #124): the hardcoded listing is retired and
        # the page composes with a Resource Bento. Seeded so the page is not
        # blank before content entry; editors reorder or replace from here.
        for page in ArticleLandingPage.objects.all():
            targets.append((page, [
                ('resource_bento', {
                    'heading': 'Featured Opinions',
                    'mode': 'manual',
                    'layout': 'duo',
                    'items': list(page.get_featured_articles()[:5]),
                    'show_header': True,
                    'show_date': True,
                    'show_author': True,
                }),
            ]))

        if not targets:
            self.stderr.write('No listing pages found; nothing to do.')
            return

        for page, body in targets:
            label = f'{page.title} ({page.url_path})'
            if page.body and not force:
                self.stdout.write(f'SKIP {label}: body already populated (pass --force).')
                continue
            self.stdout.write(f'{label}: {", ".join(t for t, _ in body)}')
            if apply:
                page.body = body
                with _quiet_search_logging():
                    page.save_revision().publish()

        if apply:
            self.stdout.write(self.style.SUCCESS('Listing page bodies seeded.'))
        else:
            self.stdout.write('(dry-run — pass --apply to write)')
