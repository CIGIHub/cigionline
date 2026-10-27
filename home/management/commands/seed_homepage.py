"""Seed the design-system homepage body with a default composition.

The homepage (`home.HomePage`) renders its `body` StreamField of DS modules. This
command populates that body with the default module stack from the design comp. Most modules auto-query, so the page renders populated without
hand-entry; program grid is scoped to a placeholder program and the image CTA and
image+text fall back to any available image, both for editors to replace.

Dry-run by default — pass --apply to write. --force overwrites a non-empty body;
--revert clears it.
"""
import logging
from contextlib import contextmanager

from django.core.management.base import BaseCommand
from wagtail.rich_text import RichText

from home.models import HomePage


@contextmanager
def _quiet_search_logging():
    """Silence the search-index logger for the duration of a publish. Publishing a
    page pushes it into the search backend; when that backend is unreachable (e.g.
    Elasticsearch is down in local dev) Wagtail catches the error but logs the full
    traceback. The publish itself still succeeds, so suppress the noise."""
    logger = logging.getLogger('modelsearch')
    previous = logger.level
    logger.setLevel(logging.CRITICAL)
    try:
        yield
    finally:
        logger.setLevel(previous)


class Command(BaseCommand):
    help = 'Seed the homepage body with the default DS module composition.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Write changes (otherwise dry-run).')
        parser.add_argument('--force', action='store_true', help='Overwrite an existing non-empty body.')
        parser.add_argument('--revert', action='store_true', help='Clear the homepage body.')

    def handle(self, *args, **options):
        home = HomePage.objects.first()
        if home is None:
            self.stderr.write('No HomePage found; nothing to do.')
            return

        apply = options['apply']

        if options['revert']:
            self.stdout.write('Reverting homepage body to empty.')
            if apply:
                home.body = []
                with _quiet_search_logging():
                    home.save_revision().publish()
                self.stdout.write(self.style.SUCCESS('Homepage body cleared.'))
            else:
                self.stdout.write('(dry-run — pass --apply to write)')
            return

        if home.body and not options['force']:
            self.stdout.write('Homepage body is already populated; pass --force to overwrite. No changes.')
            return

        body = self._composition()
        self.stdout.write(f'Prepared {len(body)} homepage sections: {", ".join(t for t, _ in body)}.')
        if not apply:
            self.stdout.write('(dry-run — pass --apply to write)')
            return

        home.body = body
        with _quiet_search_logging():
            home.save_revision().publish()
        self.stdout.write(self.style.SUCCESS('Homepage body seeded and published.'))

    def _composition(self):
        """The homepage module stack, matching the design comp.

        Most modules auto-query from just a heading. Program grid is scoped to one
        program (any live one is chosen as a default for editors to change); the
        CTA and image+text need an image and fall back to any available one.
        """
        from wagtail.images import get_image_model
        from research.models import ProjectPage, ThemePage

        image = get_image_model().objects.first()

        # Program grid is program-scoped — pick any live program as a placeholder.
        program = None
        for theme in ThemePage.objects.live().filter(archive=0).order_by('path'):
            row = theme.theme_programs.select_related('program').first()
            if row and row.program and row.program.live:
                program = row.program
                break
        if program is None:
            program = ProjectPage.objects.live().public().first()

        # Trending issues spotlights one page — point it at a recent legacy article
        # (excluding DS test/scaffold pages, which sort first by recent date).
        from articles.models import ArticlePage
        trending_item = (
            ArticlePage.objects.live().public()
            .filter(publishing_date__isnull=False, image_hero__isnull=False)
            .exclude(title__icontains='test')
            .order_by('-publishing_date').first()
        )
        trending_value = {'surface': 'dark', 'cta_label': 'Read More'}
        if trending_item is not None:
            trending_value['mode'] = 'manual'
            trending_value['item'] = trending_item
        else:
            trending_value['mode'] = 'auto'

        blocks = [
            ('primary_hero', {
                'surface': 'dark',
                'heading': 'World-leading research driving policy at the intersection '
                           'of technology and governance',
                'description': RichText(
                    '<p>CIGI produces rigorous, independent research to inform the '
                    'decisions shaping our digital future.</p>'),
            }),
            # Homepage bento = centred layout, no header.
            ('resource_bento', {
                'surface': 'dark',
                'heading': 'Latest Research and Analysis',
                'layout': 'centered',
                'show_header': False,
                'show_date': True,
                'show_author': True,
                'count': 6,
            }),
            ('trending_issues', trending_value),
            # Card slots per the homepage frame: bio + expertise on.
            # Expertise pills need `manage.py update_expert_topics` to have run.
            ('experts_carousel', {
                'surface': 'light', 'heading': 'Experts', 'cta_label': 'View All Experts',
                'show_pagination': True,
                'card_slots': {'show_title': True, 'show_bio': True,
                               'show_expertise': True, 'show_latest_activity': False,
                               'show_read_bio': False},
            }),
            # programs=[] forces the auto branch (all live programs); omitting the
            # key leaves a phantom one-empty-entry list that reads as author-curated.
            ('program_spotlight', {'heading': 'Our Research', 'programs': []}),
        ]

        # Light duo bento — replaces the program grid slot
        # per Keypage R03 (Evan, 2026-07-03). Two features + compact column.
        blocks.append(('resource_bento', {
            'surface': 'light',
            'layout': 'duo',
            'heading': 'Opinions / Thought Leadership',
            'cta_label': 'Browse All',
            'show_header': True,
            'show_date': True,
            'show_author': True,
            'count': 7,
        }))

        # "View all" points at the events listing page (the site's /events/).
        from events.models import EventListPage
        events_list = EventListPage.objects.live().order_by('path').first()
        events_value = {'surface': 'dark', 'heading': 'Events', 'cta_label': 'View all',
                        'show_pagination': True}
        if events_list is not None:
            events_value['cta_page'] = events_list
        blocks.append(('events_carousel', events_value))

        if image is not None:
            # buttons is a ListBlock — seed it explicitly (an omitted key leaves a
            # phantom one-empty-entry list that renders an empty button box). The
            # CTA button is the red-panel treatment: outline + on-red + chevron.
            from wagtail.models import Page
            dph = Page.objects.live().filter(slug='digital-policy-hub').first()
            cta_buttons = []
            if dph is not None:
                cta_buttons = [{
                    'label': 'Learn More',
                    'link_page': dph,
                    'variant': 'outline',
                    'scheme': 'on-red',
                    'icon': 'chevron',
                }]
            else:
                self.stdout.write(self.style.WARNING(
                    'No digital-policy-hub page — image CTA seeded without a button.'))
            blocks.append(('cta_image', {
                'image': image,
                'heading': 'Digital Policy Hub',
                'text': RichText(
                    '<p>A collaborative space for emerging scholars working on the '
                    'governance of digital technologies.</p>'),
                'buttons': cta_buttons,
            }))
            # Content mirrors the design node (1361:117901): two paragraphs +
            # the About CIGI outline button.
            about = Page.objects.live().filter(slug='about').first()
            image_text_buttons = []
            if about is not None:
                image_text_buttons = [{
                    'label': 'About CIGI',
                    'link_page': about,
                    'variant': 'outline',
                    'scheme': 'auto',
                    'icon': 'chevron',
                }]
            blocks.append(('image_text', {
                'image': image,
                'heading': 'Beyond the Research',
                'body': RichText(
                    '<p>The Centre for International Governance Innovation (CIGI) is '
                    'an independent, non-partisan think tank whose peer-reviewed '
                    'research, foresight and trusted analysis influence policy makers '
                    'to innovate.</p>'
                    '<p>CIGI tackles the governance challenges and opportunities of '
                    'data and transformative technologies and their impact on the '
                    'economy, security, democracy, and societies.</p>'),
                'buttons': image_text_buttons,
            }))
        else:
            self.stdout.write(self.style.WARNING(
                'No images in the DB — image CTA / image+text modules skipped.'))

        return blocks
