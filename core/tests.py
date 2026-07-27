from django import forms
from django.utils import timezone
from articles.models import ArticleListPage, ArticlePage, ArticleTypePage
from annual_reports.models import AnnualReportListPage
from careers.models import JobPostingListPage
from home.models import HomePage, Think7HomePage
from people.models import PersonListPage
from research.models import (
    ProjectPage,
)
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from .wagtail_hooks import get_filter_purge_cache_urls, get_purge_cache_url
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


class BasicPageTests(WagtailPageTestCase):
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
