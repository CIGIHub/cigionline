from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from articles.models import ArticlePage, ArticleTypePage
from home.models import HomePage
from publications.models import PublicationPage, PublicationTypePage
from research.models import ProjectPage, ThemePage, ThemeProgram, TopicPage
from streams.blocks import FacetedListingBlock, ResourceBentoBlock

from .cards import page_pills
from .router_links import clear_cache


class ThemeFacetedListingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        home = HomePage.objects.get()
        block = FacetedListingBlock()
        cls.listing = block.get_prep_value(block.to_python({
            'card_type': 'resource',
            'prefix': 'theme',
            'program_source': 'auto',
        }))
        cls.theme = home.add_child(instance=ThemePage(
            title='Theme listing',
            slug='theme-listing',
            body=[{'type': 'faceted_listing', 'value': cls.listing}],
        ))
        other_theme = home.add_child(instance=ThemePage(
            title='Other theme', slug='other-theme'))
        cls.topic = home.add_child(instance=TopicPage(
            title='Mapped topic', slug='mapped-topic', program_theme=cls.theme))
        other_topic = home.add_child(instance=TopicPage(
            title='Other topic', slug='other-topic', program_theme=other_theme))
        publication_type = home.add_child(instance=PublicationTypePage(
            title='Policy Briefs', slug='theme-listing-policy-briefs'))

        cls.topic_page = home.add_child(instance=PublicationPage(
            title='Included through its topic',
            slug='included-through-topic',
            publication_type=publication_type,
            publishing_date=timezone.now(),
        ))
        cls.topic_page.topics.set([cls.topic])
        cls.topic_page.save()

        project = home.add_child(instance=ProjectPage(
            title='Theme program',
            slug='theme-program',
            publishing_date=timezone.now(),
        ))
        ThemeProgram.objects.create(theme=cls.theme, program=project)
        cls.program_only_page = home.add_child(instance=PublicationPage(
            title='Excluded program-only page',
            slug='excluded-program-only-page',
            publication_type=publication_type,
            publishing_date=timezone.now(),
        ))
        cls.program_only_page.projects.set([project])
        cls.program_only_page.topics.set([other_topic])
        cls.program_only_page.save()

    def setUp(self):
        clear_cache()

    def test_listing_follows_topics_to_theme_and_applies_topic_filter(self):
        response = self.client.get(
            self.theme.url,
            {'theme-topic': self.topic.pk},
        )

        self.assertContains(response, self.topic_page.title)
        self.assertNotContains(response, self.program_only_page.title)
        self.assertContains(response, 'type="search" name="theme-q"')
        self.assertContains(
            response,
            f'name="theme-topic" value="{self.topic.pk}" checked',
        )

    def test_topic_pill_links_to_the_filtered_theme_listing(self):
        theme_path = self.theme.get_url_parts()[2]
        self.assertEqual(page_pills(self.topic_page), [{
            'label': self.topic.title,
            'accent': 'red',
            'url': (
                f'{theme_path}?theme-topic={self.topic.pk}'
                '#router-theme'
            ),
        }])

    def test_auto_bento_uses_listing_theme_scope_and_eligibility(self):
        home = HomePage.objects.get()
        opinion_type = home.add_child(instance=ArticleTypePage(
            title='Opinion', slug='theme-test-opinion'))
        news_type = home.add_child(instance=ArticleTypePage(
            title='CIGI News', slug='news-release'))
        second_topic = home.add_child(instance=TopicPage(
            title='Second mapped topic', slug='second-mapped-topic',
            program_theme=self.theme))
        article = home.add_child(instance=ArticlePage(
            title='Topic-only opinion', slug='topic-only-opinion',
            article_type=opinion_type, publishing_date=timezone.now() + timedelta(days=1)))
        article.topics.set([self.topic, second_topic])
        article.save()
        undated = home.add_child(instance=ArticlePage(
            title='Undated opinion', slug='undated-opinion',
            article_type=opinion_type, publishing_date=timezone.now()))
        undated.topics.set([self.topic])
        undated.save()
        ArticlePage.objects.filter(pk=undated.pk).update(publishing_date=None)
        news = home.add_child(instance=ArticlePage(
            title='Theme news', slug='theme-news',
            article_type=news_type, publishing_date=timezone.now()))
        news.topics.set([self.topic])
        news.save()

        block = ResourceBentoBlock()
        value = block.to_python({'mode': 'auto', 'count': 9})
        context = block.get_context(value, {'page': self.theme})
        pages = [context['feature']] + context['compact_cards']
        self.assertEqual(
            [page.pk for page in pages],
            [article.pk, self.topic_page.pk, undated.pk],
        )

        response = self.client.get(self.theme.url)
        for page in (article, self.topic_page, undated):
            self.assertContains(response, page.title)
        for page in (news, self.program_only_page):
            self.assertNotContains(response, page.title)

        value = block.to_python({
            'mode': 'auto', 'count': 9, 'content_types': ['publication'],
        })
        context = block.get_context(value, {'page': self.theme})
        self.assertEqual(context['feature'].pk, self.topic_page.pk)
        self.assertEqual(context['compact_cards'], [])

    def test_manual_bento_keeps_editor_selected_program_only_page(self):
        block = ResourceBentoBlock()
        value = block.to_python({
            'mode': 'manual', 'items': [self.program_only_page.pk],
        })

        context = block.get_context(value, {'page': self.theme})
        self.assertEqual(context['feature'].pk, self.program_only_page.pk)
        self.assertEqual(context['compact_cards'], [])
