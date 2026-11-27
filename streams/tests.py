from datetime import timedelta
from types import SimpleNamespace
from unittest import mock

from django.core.exceptions import ValidationError
from django.template.loader import render_to_string

from articles.models import ArticlePage, ArticleTypePage
from core.models import Theme
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.utils import timezone
from events.models import EventPage
from home.models import HomePage
from multimedia.models import MultimediaPage
from people.models import PeoplePage, PersonPage, PersonType
from publications.models import PublicationPage, PublicationTypePage
from research.models import ProjectPage, ThemePage, ThemeProgram, TopicPage
from wagtail import blocks

from .blocks import (
    AccordionBlock,
    AutoPlayVideoBlock,
    ButtonBlock,
    ChartBlock,
    CollapsibleParagraphBlock,
    EmbeddedMultimediaBlock,
    EmbeddedVideoBlock,
    ExternalQuoteBlock,
    ExternalVideoBlock,
    ExtractBlock,
    ExpertsCarouselBlock,
    FilesBlock,
    HighlightTitleBlock,
    InlineVideoBlock,
    InteractiveChartBlock,
    NewsletterSubscriptionBlock,
    ParagraphBlock,
    ResourceCarouselBlock,
    TextBorderBlock,
    TooltipBlock,
    TweetBlock,
)


class AutoPlayVideoBlockTests(SimpleTestCase):
    def test_uses_dph_page_template(self):
        page = SimpleNamespace(
            _meta=SimpleNamespace(verbose_name='Page'),
            theme=SimpleNamespace(name='DPH'),
        )

        self.assertEqual(
            AutoPlayVideoBlock().get_template({}, {'page': page}),
            'themes/dph/streams/page_autoplay_video_block.html',
        )

    def test_autoplay_can_be_disabled(self):
        value = SimpleNamespace(
            video=SimpleNamespace(url='/media/video.mp4'),
            caption='Video caption',
            disable_autoplay=True,
        )

        for template in (
            'streams/autoplay_video_block.html',
            'streams/legacy/autoplay_video_block.html',
            'themes/dph/streams/page_autoplay_video_block.html',
        ):
            with self.subTest(template=template):
                html = render_to_string(template, {'self': value})
                self.assertIn('<video playsinline muted controls', html)
                self.assertNotIn(' autoplay', html)


class AccordionBlockTests(SimpleTestCase):
    def test_rich_text_supports_images(self):
        self.assertIn('image', AccordionBlock().child_blocks['text'].features)


class ExpertsCarouselBlockTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        home = HomePage.objects.get()
        cls.theme = home.add_child(instance=ThemePage(
            title='AI and Technology', slug='ai-and-technology'))
        cls.topic = home.add_child(instance=TopicPage(
            title='Artificial Intelligence', slug='artificial-intelligence',
            program_theme=cls.theme))
        cls.program = home.add_child(instance=ProjectPage(
            title='AI Program', slug='ai-program', publishing_date=timezone.now()))
        people = home.add_child(instance=PeoplePage(title='People', slug='people'))
        expert_type = PersonType.objects.get(name='Expert')

        def expert(name):
            person = people.add_child(instance=PersonPage(
                title=name, slug=name.lower().replace(' ', '-'), last_name=name))
            person.person_types.set([expert_type])
            person.save()
            return person

        cls.theme_expert = expert('Theme Expert')
        cls.theme_expert.derived_topics.set([cls.topic])
        cls.program_expert = expert('Program Expert')
        cls.program_expert.projects.set([cls.program])
        cls.program_expert.save()
        cls.other_expert = expert('Other Expert')

    @staticmethod
    def experts(mode, page):
        block = ExpertsCarouselBlock()
        value = block.to_python({'mode': mode, 'count': 12})
        return block.get_context(value, {'page': page})['experts']

    def test_offers_theme_and_program_population_modes(self):
        choices = dict(ExpertsCarouselBlock().child_blocks['mode'].field.choices)

        self.assertIn('theme', choices)
        self.assertIn('program', choices)

    def test_theme_mode_only_returns_experts_associated_with_current_theme(self):
        self.assertEqual(self.experts('theme', self.theme), [self.theme_expert])

    def test_program_mode_only_returns_experts_associated_with_current_program(self):
        self.assertEqual(self.experts('program', self.program), [self.program_expert])

    def test_scoped_modes_return_nothing_on_the_wrong_page_type(self):
        self.assertEqual(self.experts('theme', self.program), [])
        self.assertEqual(self.experts('program', self.theme), [])


class ResourceCarouselBlockTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        home = HomePage.objects.get()
        now = timezone.now()
        cls.theme = home.add_child(instance=ThemePage(
            title='Shared Theme', slug='shared-theme'))
        cls.current_program = home.add_child(instance=ProjectPage(
            title='Current Program', slug='current-program', publishing_date=now))
        cls.sibling_program = home.add_child(instance=ProjectPage(
            title='Sibling Program', slug='sibling-program', publishing_date=now))
        ThemeProgram.objects.create(theme=cls.theme, program=cls.current_program)
        ThemeProgram.objects.create(theme=cls.theme, program=cls.sibling_program)
        article_type = home.add_child(instance=ArticleTypePage(
            title='Resource Opinion', slug='resource-opinion'))

        def article(title, days_old, program):
            page = home.add_child(instance=ArticlePage(
                title=title,
                slug=title.lower().replace(' ', '-'),
                article_type=article_type,
                publishing_date=now - timedelta(days=days_old),
            ))
            page.projects.set([program])
            page.save()
            return page

        cls.recent_one = article('Recent One', 2, cls.sibling_program)
        cls.recent_two = article('Recent Two', 20, cls.sibling_program)
        cls.newest_backfill = article('Newest Backfill', 31, cls.sibling_program)
        cls.older_backfill = article('Older Backfill', 60, cls.sibling_program)
        cls.current_content = article('Current Content', 1, cls.current_program)

    def pages(self, page=None, count=3):
        block = ResourceCarouselBlock()
        value = block.to_python({'mode': 'theme_random', 'count': count})
        context = block.get_context(value, {'page': page or self.current_program})
        return [p for p in [context['feature'], *context['compact_cards']] if p]

    def test_random_theme_mode_prioritizes_recent_sibling_content_then_backfills(self):
        pages = self.pages()

        self.assertEqual(set(pages[:2]), {self.recent_one, self.recent_two})
        self.assertEqual(pages[2], self.newest_backfill)
        self.assertNotIn(self.older_backfill, pages)
        self.assertNotIn(self.current_content, pages)

    def test_offers_random_theme_population_mode(self):
        choices = dict(ResourceCarouselBlock().child_blocks['mode'].field.choices)

        self.assertIn('theme_random', choices)

    def test_random_theme_mode_returns_nothing_without_a_program_theme(self):
        unthemed = HomePage.objects.get().add_child(instance=ProjectPage(
            title='Unthemed Program', slug='unthemed-program',
            publishing_date=timezone.now()))

        self.assertEqual(self.pages(unthemed), [])


class LegacyBlockTemplateTests(TestCase):
    """A page rendering its pre-redesign theme fork renders the pre-redesign
    block templates (streams/legacy/); DS pages, DS hybrids (DPH publication
    and event) and themes without a fork keep the DS blocks (John, BugHerd
    #522). Builds its own pages — no people.json fixture."""

    LEGACY_BLOCKS = {
        AutoPlayVideoBlock: 'autoplay_video_block',
        ChartBlock: 'chart_block',
        CollapsibleParagraphBlock: 'collapsible_paragraph_block',
        EmbeddedMultimediaBlock: 'embedded_multimedia_block',
        EmbeddedVideoBlock: 'embedded_video_block',
        ExternalQuoteBlock: 'external_quote_block',
        ExternalVideoBlock: 'external_video_block',
        ExtractBlock: 'extract_block',
        FilesBlock: 'files_block',
        HighlightTitleBlock: 'highlight_title_block',
        InlineVideoBlock: 'inline_video_block',
        NewsletterSubscriptionBlock: 'newsletter_subscription_block',
        TextBorderBlock: 'text_border_block',
        TooltipBlock: 'tool_tip_block',
        TweetBlock: 'tweet_block',
    }

    @classmethod
    def setUpTestData(cls):
        cls.home = HomePage.objects.get()
        cls.article_type = cls.home.add_child(instance=ArticleTypePage(title='Opinion', slug='opinion-type'))

    def theme(self, name):
        return Theme.objects.create(name=name)

    def article(self, theme_name=None):
        theme = self.theme(theme_name) if theme_name else None
        return self.home.add_child(instance=ArticlePage(
            title=f'Article {theme_name}', slug=f'article-{theme_name or "unthemed"}'.lower().replace(' ', '-'),
            theme=theme, article_type=self.article_type, publishing_date=timezone.now()))

    def event(self, theme_name):
        return self.home.add_child(instance=EventPage(
            title=f'Event {theme_name}', slug=f'event-{theme_name}'.lower().replace(' ', '-'),
            theme=self.theme(theme_name), publishing_date=timezone.now()))

    def publication(self, theme_name):
        return self.home.add_child(instance=PublicationPage(
            title=f'Publication {theme_name}', slug=f'publication-{theme_name}'.lower().replace(' ', '-'),
            theme=self.theme(theme_name), publishing_date=timezone.now(),
            publication_type=self.home.add_child(instance=PublicationTypePage(title='Working Paper', slug='working-paper'))))

    def render_chart(self, page):
        block = ChartBlock()
        value = block.to_python({'title': 'Figure 1: X', 'image': None, 'hide_image_caption': False, 'full_width': False})
        return block.render(value, context={'page': page})

    def render_files(self, page):
        block = FilesBlock()
        return block.render(block.to_python({'files': []}), context={'page': page})

    def render_collapsible(self, page):
        block = CollapsibleParagraphBlock()
        value = block.to_python({'collapsed': True, 'title': '<p>More</p>', 'title_type': 'h2', 'paragraph': '<p>Body</p>'})
        return block.render(value, context={'page': page})

    def assertLegacyChart(self, html):
        self.assertIn('<div class="container">', html)
        self.assertIn('<div class="stream-block-chart">', html)
        self.assertNotIn('ds-prose__chart', html)

    def assertDSChart(self, html):
        self.assertIn('ds-prose__chart', html)
        self.assertNotIn('stream-block-chart', html)

    def test_legacy_theme_article_renders_legacy_chart(self):
        # The ticket's page: a Data Value Series article.
        page = self.article('Data Value Series')
        self.assertTrue(page.renders_legacy_fork)
        self.assertLegacyChart(self.render_chart(page))

    def test_legacy_fork_picks_every_restored_block_template(self):
        page = self.article('Data Value Series')
        for block_class, name in self.LEGACY_BLOCKS.items():
            with self.subTest(block=block_class.__name__):
                self.assertEqual(
                    block_class().get_template(None, {'page': page}),
                    f'streams/legacy/{name}.html')

    def test_legacy_fork_keeps_ds_template_for_blocks_with_no_legacy_copy(self):
        # Paragraph never diverged — no legacy copy, so it stays standard.
        page = self.article('Data Value Series')
        self.assertEqual(
            ParagraphBlock().get_template(None, {'page': page}), 'streams/paragraph_block.html')

    def test_unthemed_article_renders_ds_chart(self):
        page = self.article()
        self.assertFalse(page.renders_legacy_fork)
        self.assertDSChart(self.render_chart(page))

    def test_theme_without_fork_renders_ds_chart(self):
        # Responsible Technology carries a theme but has no article fork.
        page = self.article('Responsible Technology')
        self.assertFalse(page.renders_legacy_fork)
        self.assertDSChart(self.render_chart(page))

    def test_theme_specific_override_wins_over_legacy(self):
        page = self.article('Cyber Series')
        self.assertTrue(page.renders_legacy_fork)
        self.assertEqual(
            ChartBlock().get_template(None, {'page': page}),
            'themes/cyber_series/streams/opinion_chart_block.html')
        # A block with no Cyber Series override falls to the legacy copy.
        self.assertEqual(
            TweetBlock().get_template(None, {'page': page}), 'streams/legacy/tweet_block.html')

    def test_dph_publication_is_ds(self):
        page = self.publication('DPH')
        self.assertEqual(page.get_template(RequestFactory().get('/')), 'themes/dph/publication_page.html')
        self.assertFalse(page.renders_legacy_fork)
        self.assertDSChart(self.render_chart(page))
        self.assertNotIn('<div class="container files-block">', self.render_files(page))

    def test_dph_event_is_ds(self):
        # themes/dph/event_page.html extends the DS event single.
        page = self.event('DPH')
        self.assertEqual(page.get_template(RequestFactory().get('/')), 'themes/dph/event_page.html')
        self.assertFalse(page.renders_legacy_fork)
        self.assertDSChart(self.render_chart(page))
        self.assertNotIn('<div class="container files-block">', self.render_files(page))

    def test_digital_finance_event_renders_legacy_blocks(self):
        page = self.event('Digital Finance')
        self.assertTrue(page.renders_legacy_fork)
        self.assertIn('<div class="container files-block">', self.render_files(page))
        html = self.render_collapsible(page)
        self.assertIn('<div class="collapsible-paragraph-block collapsed">', html)
        self.assertIn('<div class="container">', html)

    def test_themed_episode_renders_legacy_fork(self):
        page = self.home.add_child(instance=MultimediaPage(
            title='Episode', slug='episode', theme=self.theme('Policy Prompt'), publishing_date=timezone.now()))
        self.assertTrue(page.renders_legacy_fork)
        unthemed = self.home.add_child(instance=MultimediaPage(
            title='Episode 2', slug='episode-2', publishing_date=timezone.now()))
        self.assertFalse(unthemed.renders_legacy_fork)

    def test_no_page_in_context_renders_ds(self):
        for context in (None, {}, {'request': None}, {'page': None}):
            with self.subTest(context=context):
                self.assertEqual(
                    ChartBlock().get_template(None, context), 'streams/chart_block.html')
                self.assertEqual(
                    FilesBlock().get_template(None, context), 'streams/files_block.html')

    def test_think7_keeps_standard_template_without_a_think7_copy(self):
        page = self.article()
        think7 = mock.Mock(site_name='Think 7 Canada')
        with mock.patch.object(ArticlePage, 'get_site', return_value=think7):
            self.assertEqual(
                FilesBlock().get_template(None, {'page': page}), 'streams/files_block.html')
            self.assertEqual(
                ParagraphBlock().get_template(None, {'page': page}), 'think7/streams/paragraph_block.html')

    def project(self, theme_name=None):
        theme = self.theme(theme_name) if theme_name else None
        return self.home.add_child(instance=ProjectPage(
            title=f'Project {theme_name}', slug=f'project-{theme_name or "program"}'.lower().replace(' ', '-'),
            theme=theme, publishing_date=timezone.now()))

    def render_text_border(self, page):
        block = TextBorderBlock()
        value = block.to_python({'text': '<p>Bordered</p>', 'border_colour': ''})
        return block.render(value, context={'page': page})

    def test_fork_project_renders_legacy_blocks(self):
        # GES, Freedom of Thought and NSS each carry an embedded_video in a
        # pre-redesign project fork on staging.
        for theme_name in ('GES', 'Freedom of Thought', 'NSS', 'IGC'):
            with self.subTest(theme=theme_name):
                page = self.project(theme_name)
                self.assertEqual(page.get_template(RequestFactory().get('/')), page.theme_fork_template())
                self.assertTrue(page.renders_legacy_fork)
                self.assertEqual(
                    EmbeddedVideoBlock().get_template(None, {'page': page}),
                    'streams/legacy/embedded_video_block.html')
                self.assertIn('<div class="text-border-block">', self.render_text_border(page))

    def test_project_without_fork_stays_ds(self):
        # Program pages (unthemed, the DS project layout) and Responsible
        # Technology (theme, no fork).
        for theme_name in (None, 'Responsible Technology'):
            with self.subTest(theme=theme_name):
                page = self.project(theme_name)
                self.assertEqual(page.get_template(RequestFactory().get('/')), 'research/project_page.html')
                self.assertFalse(page.renders_legacy_fork)
                self.assertEqual(
                    EmbeddedVideoBlock().get_template(None, {'page': page}),
                    'streams/embedded_video_block.html')
                self.assertNotIn('text-border-block', self.render_text_border(page))


class ButtonBlockTests(SimpleTestCase):
    def test_requires_a_link_target(self):
        with self.assertRaises(blocks.StructBlockValidationError):
            ButtonBlock().clean({
                'label': 'Read more',
                'link_page': None,
                'link_document': None,
                'link_url': '',
            })


class InteractiveChartBlockTests(SimpleTestCase):
    def setUp(self):
        self.block = InteractiveChartBlock()

    def test_parses_multiple_data_series(self):
        parsed = self.block.parse_csv(
            'Year,Revenue,Expenses\n2024,12.5,8\n2025,15,9'
        )

        self.assertEqual(parsed['headers'], ['Year', 'Revenue', 'Expenses'])
        self.assertEqual(parsed['labels'], ['2024', '2025'])
        self.assertEqual(parsed['series'], [[12.5, 15], [8, 9]])

    def test_parses_semicolon_delimited_data(self):
        parsed = self.block.parse_csv('Region;Revenue\n"North, America";12.5\nEurope;15')

        self.assertEqual(parsed['labels'], ['North, America', 'Europe'])
        self.assertEqual(parsed['series'], [[12.5, 15]])

    def test_parses_tab_delimited_data(self):
        parsed = self.block.parse_csv('Year\tRevenue\tExpenses\n2024\t12.5\t8\n2025\t15\t9')

        self.assertEqual(parsed['headers'], ['Year', 'Revenue', 'Expenses'])
        self.assertEqual(parsed['series'], [[12.5, 15], [8, 9]])

    def test_allows_missing_data_points(self):
        parsed = self.block.parse_csv('Year,Revenue\n2024,\n2025,15')

        self.assertEqual(parsed['series'], [[None, 15]])

    def test_rejects_non_numeric_data(self):
        with self.assertRaisesMessage(ValidationError, 'row 2, column 2 must be a number'):
            self.block.parse_csv('Year,Revenue\n2024,nope')

    def test_rejects_inconsistent_rows(self):
        with self.assertRaisesMessage(ValidationError, 'row 2 has 2 columns; expected 3'):
            self.block.parse_csv('Year,Revenue,Expenses\n2024,12')

    def test_allows_up_to_one_thousand_data_rows(self):
        csv_data = 'Index,Value\n' + '\n'.join(f'{index},{index}' for index in range(1000))

        parsed = self.block.parse_csv(csv_data)

        self.assertEqual(len(parsed['table_rows']), 1000)

    def test_rejects_more_than_one_thousand_data_rows(self):
        csv_data = 'Index,Value\n' + '\n'.join(f'{index},{index}' for index in range(1001))

        with self.assertRaisesMessage(ValidationError, 'more than 1,000 data rows'):
            self.block.parse_csv(csv_data)

    def test_renders_chart_config_and_accessible_table(self):
        value = self.block.to_python({
            'title': 'Annual revenue',
            'description': 'Revenue increased.',
            'caption': 'Source: CIGI',
            'chart_type': 'bar',
            'csv_data': 'Year,Revenue\n2024,12',
            'full_width': False,
        })

        html = self.block.render(value)

        self.assertIn('class="interactive-chart"', html)
        self.assertIn('aria-labelledby=', html)
        self.assertIn('type="application/json"', html)
        self.assertIn('View chart data', html)
        self.assertIn('<th scope="row">2024</th>', html)

    def test_can_hide_chart_data_table(self):
        value = self.block.to_python({
            'title': 'Annual revenue',
            'description': 'Revenue increased.',
            'caption': '',
            'chart_type': 'bar',
            'csv_data': 'Year,Revenue\n2024,12',
            'show_chart_data': False,
            'full_width': False,
        })

        html = self.block.render(value)

        self.assertNotIn('View chart data', html)
        self.assertNotIn('<table>', html)
