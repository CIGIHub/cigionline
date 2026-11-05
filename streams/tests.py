from unittest import mock

from articles.models import ArticlePage, ArticleTypePage
from core.models import Theme
from django.test import RequestFactory, TestCase
from django.utils import timezone
from events.models import EventPage
from home.models import HomePage
from multimedia.models import MultimediaPage
from publications.models import PublicationPage, PublicationTypePage
from research.models import ProjectPage

from .blocks import (
    AutoPlayVideoBlock,
    ChartBlock,
    CollapsibleParagraphBlock,
    EmbeddedMultimediaBlock,
    EmbeddedVideoBlock,
    ExternalQuoteBlock,
    ExternalVideoBlock,
    ExtractBlock,
    FilesBlock,
    HighlightTitleBlock,
    InlineVideoBlock,
    NewsletterSubscriptionBlock,
    ParagraphBlock,
    TextBorderBlock,
    TooltipBlock,
    TweetBlock,
)


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
