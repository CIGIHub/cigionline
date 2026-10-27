from django.core.management.base import BaseCommand
from wagtail.contrib.redirects.models import Redirect
from wagtail.models import Site

# Cutover redirect map (docs/redesign/close-out.md #4). Safe to load ahead of
# cutover: the redirects middleware only fires on 404s, so each entry stays
# dormant until its legacy page is unpublished. Topic-consolidation redirects
# are created by `consolidate_topics` itself and are not repeated here.
#
# /about/venue-rentals/ is the DESIGNATED path for the author-built venue
# landing page (replacing the legacy FacilityRentalsPage) — the content-entry
# team must create it there (communicated by Evan, 2026-07-08).
REDIRECTS = [
    # Legacy ArticleTypePage listings → new router pages.
    ('/articles/cigi-in-the-news/', '/in-the-news/'),
    ('/articles/news-release/', '/cigi-news/'),
    # Opinion-type listings have no dedicated router — all articles are the
    # opinion/article template; closest archive is the Opinion-filtered search.
    ('/articles/op-eds/', '/search/?contenttype=Opinion'),
    ('/articles/interviews/', '/search/?contenttype=Opinion'),
    ('/articles/opinion/', '/search/?contenttype=Opinion'),
    ('/articles/essays/', '/search/?contenttype=Opinion'),
    # Legacy self-serving venue page → the authored venue landing.
    ('/about/facility-rentals', '/about/venue-rentals/'),
]


class Command(BaseCommand):
    help = (
        'Load the cutover redirect map (wagtail.contrib.redirects). Idempotent; '
        'dry-run by default — pass --apply to write.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Execute writes (default: dry-run).')

    def handle(self, *args, **options):
        site = Site.objects.get(is_default_site=True)
        for old_path, link in REDIRECTS:
            normalised = Redirect.normalise_path(old_path)
            existing = Redirect.objects.filter(site=site, old_path=normalised).first()
            if existing and existing.redirect_link == link:
                self.stdout.write(f'ok        {normalised} -> {link}')
                continue
            action = 'update' if existing else 'create'
            self.stdout.write(f'{action:9} {normalised} -> {link}')
            if options['apply']:
                Redirect.objects.update_or_create(
                    site=site, old_path=normalised,
                    defaults={'redirect_link': link, 'is_permanent': True},
                )
        if not options['apply']:
            self.stdout.write(self.style.WARNING('Dry run — pass --apply to write.'))
