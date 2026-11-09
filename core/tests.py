import datetime
from xml.etree import ElementTree

from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.utils import timezone
from articles.models import ArticleListPage, ArticlePage, ArticleTypePage
from annual_reports.models import AnnualReportListPage
from careers.models import JobPostingListPage
from home.models import HomePage, Think7HomePage
from multimedia.models import MultimediaListPage, MultimediaPage
from people.models import PersonListPage
from publications.models import PublicationListPage, PublicationPage, PublicationTypePage
from research.models import (
    ProjectPage,
)
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from .wagtail_hooks import (
    clear_template_fragment_cache,
    get_filter_purge_cache_urls,
    get_purge_cache_url,
)
from .models import (
    BasicPage,
    FacilityRentalsPage,
    FundingPage,
    HumanAnalysisStandardPage,
    PrivacyNoticePage,
    Theme,
    TwentyFifthPageSingleton,
    TwentiethPage,
    TwentiethPageSingleton,
)


class PurgeCloudflareCacheTests(WagtailPageTestCase):
    def setUp(self):
        Site.objects.update(hostname='www.cigionline.org', port=443)

    def test_get_purge_cache_url_accepts_full_urls(self):
        url = 'https://www.cigionline.org/articles/example/'

        self.assertEqual(get_purge_cache_url(url), url)

    def test_get_purge_cache_url_uses_default_site_for_paths(self):
        self.assertEqual(
            get_purge_cache_url('/articles/example/'),
            'https://www.cigionline.org/articles/example/',
        )

    def test_get_purge_cache_url_ignores_blank_lines(self):
        self.assertIsNone(get_purge_cache_url('   '))

    def test_get_purge_cache_url_rejects_invalid_input(self):
        with self.assertRaises(forms.ValidationError):
            get_purge_cache_url('articles/example/')

    def test_get_filter_purge_cache_urls_filters_articles_by_theme_and_article_type(self):
        site = Site.objects.get(is_default_site=True)
        home_page = HomePage(title='Test Home')
        site.root_page.add_child(instance=home_page)
        site.root_page = home_page
        site.save()

        article_list = ArticleListPage(title='Opinions')
        home_page.add_child(instance=article_list)

        article_type = ArticleTypePage(title='Op-Eds')
        article_list.add_child(instance=article_type)

        theme = Theme.objects.create(name='Policy Prompt')
        matching_article = ArticlePage(
            title='Matching Article',
            article_type=article_type,
            theme=theme,
            publishing_date=timezone.now(),
        )
        article_list.add_child(instance=matching_article)

        other_article = ArticlePage(
            title='Other Article',
            article_type=article_type,
            publishing_date=timezone.now(),
        )
        article_list.add_child(instance=other_article)

        urls = get_filter_purge_cache_urls({
            'page_types': ['articles.ArticlePage'],
            'themes': [theme],
            'article_types': [article_type],
        })

        self.assertEqual(urls, [matching_article.get_full_url()])

    def test_clear_template_fragment_cache_deletes_known_fragment(self):
        footer_key = make_template_fragment_key('footer')
        homepage_footer_key = make_template_fragment_key('footer_homepage')
        cache.set(footer_key, 'cached footer')
        cache.set(homepage_footer_key, 'cached homepage footer')

        clear_template_fragment_cache('footer')

        self.assertIsNone(cache.get(footer_key))
        self.assertIsNone(cache.get(homepage_footer_key))

    def test_clear_template_fragment_cache_rejects_unknown_fragment(self):
        with self.assertRaises(forms.ValidationError):
            clear_template_fragment_cache('unknown')


class LatestContentFeedTests(WagtailPageTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='feed-editor')
        self.site = Site.objects.get(is_default_site=True)
        self.home_page = self._publish(self.site.root_page, HomePage(title='Feed Home'))
        self.site.root_page = self.home_page
        self.site.hostname = 'www.cigionline.org'
        self.site.port = 443
        self.site.save()

        self.article_list = self._publish(self.home_page, ArticleListPage(title='Opinions'))
        self.article_type = self._publish(self.article_list, ArticleTypePage(title='Opinion'))
        self.news_type = self._publish(self.article_list, ArticleTypePage(title='CIGI in the News'))

        self.publication_list = self._publish(self.home_page, PublicationListPage(title='Publications'))
        self.publication_type = self._publish(
            self.publication_list,
            PublicationTypePage(title='Policy Briefs'),
        )
        self.multimedia_list = self._publish(self.home_page, MultimediaListPage(title='Multimedia'))

    def _publish(self, parent, page):
        page.owner = self.user
        parent.add_child(instance=page)
        page.save_revision(user=self.user).publish()
        return page

    def _item_titles(self, response):
        root = ElementTree.fromstring(response.content)
        return [item.findtext('title') for item in root.findall('./channel/item')]

    def test_feed_contains_requested_content_types_newest_first(self):
        now = timezone.now()
        self._publish(
            self.article_list,
            ArticlePage(
                title='Feed Article',
                article_type=self.article_type,
                publishing_date=now - datetime.timedelta(days=3),
                short_description='<b>Article summary</b>',
            ),
        )
        self._publish(
            self.publication_list,
            PublicationPage(
                title='Feed Publication',
                publication_type=self.publication_type,
                publishing_date=now - datetime.timedelta(days=2),
            ),
        )
        self._publish(
            self.multimedia_list,
            MultimediaPage(
                title='Feed Multimedia',
                publishing_date=now - datetime.timedelta(days=1),
            ),
        )

        response = self.client.get('/feed/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/rss+xml'))
        self.assertEqual(
            self._item_titles(response),
            ['Feed Multimedia', 'Feed Publication', 'Feed Article'],
        )
        self.assertContains(response, 'Article summary')
        self.assertNotContains(response, '&lt;b&gt;Article summary&lt;/b&gt;')

    def test_feed_excludes_future_draft_external_news_and_unroutable_items(self):
        now = timezone.now()
        self._publish(
            self.multimedia_list,
            MultimediaPage(
                title='Future Multimedia',
                publishing_date=now + datetime.timedelta(days=1),
            ),
        )
        self._publish(
            self.article_list,
            ArticlePage(
                title='External News',
                article_type=self.news_type,
                publishing_date=now,
            ),
        )
        self.article_list.add_child(
            instance=ArticlePage(
                title='Draft Article',
                article_type=self.article_type,
                publishing_date=now,
                live=False,
                owner=self.user,
            ),
        )
        unroutable = self._publish(
            self.publication_list,
            PublicationPage(
                title='Unroutable Publication',
                publication_type=self.publication_type,
                publishing_date=now,
            ),
        )
        Page.objects.filter(pk=unroutable.pk).update(url_path='/stale-path/')

        response = self.client.get('/feed/')

        self.assertEqual(self._item_titles(response), [])


class BasicPageTests(WagtailPageTestCase):
    def test_body_includes_interactive_chart(self):
        body = BasicPage._meta.get_field('body')

        self.assertIn('interactive_chart', body.stream_block.child_blocks)

    def test_basicpage_parent_page_types(self):
        """
        Verify allowed parent page types.
        """
        self.assertAllowedParentPageTypes(
            BasicPage,
            {BasicPage, HomePage, JobPostingListPage, Think7HomePage}
        )

    def test_basicpage_child_page_types(self):
        """
        Verify allowed child page types.
        """
        self.assertAllowedSubpageTypes(
            BasicPage,
            {
                AnnualReportListPage,
                BasicPage,
                FacilityRentalsPage,
                FundingPage,
                HumanAnalysisStandardPage,
                PersonListPage,
                ProjectPage,
                TwentiethPage,
                TwentiethPageSingleton,
            }
        )


class TwentyFifthPageSingletonTests(WagtailPageTestCase):
    def test_twentyfifthpagesingleton_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            TwentyFifthPageSingleton,
            {HomePage},
        )

    def test_twentyfifthpagesingleton_child_page_types(self):
        self.assertAllowedSubpageTypes(
            TwentyFifthPageSingleton,
            {},
        )


class FundingPageTests(WagtailPageTestCase):
    def test_fundingpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            FundingPage,
            {BasicPage},
        )

    def test_fundingpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            FundingPage,
            {},
        )


class HumanAnalysisStandardPageTests(WagtailPageTestCase):
    def test_humananalysisstandardpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            HumanAnalysisStandardPage,
            {BasicPage},
        )

    def test_humananalysisstandardpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            HumanAnalysisStandardPage,
            {},
        )


class PrivacyNoticePageTests(WagtailPageTestCase):
    def test_privacynoticepage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PrivacyNoticePage,
            {HomePage},
        )

    def test_privacynoticepage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PrivacyNoticePage,
            {},
        )
