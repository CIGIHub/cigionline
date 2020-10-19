from core.models import HomePage
from wagtail.tests.utils import WagtailPageTests

from .models import ArticleLandingPage, ArticleListPage, ArticlePage


class ArticleLandingPageTests(WagtailPageTests):
    def test_articlelandingpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            ArticleLandingPage,
            {HomePage},
        )

    def test_articlelandingpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            ArticleLandingPage,
            {},
        )


class ArticleListPageTests(WagtailPageTests):
    def test_articlelistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            ArticleListPage,
            {HomePage},
        )

    def test_articlelistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            ArticleListPage,
            {ArticlePage},
        )


class ArticlePageTests(WagtailPageTests):
    def test_articlepage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            ArticlePage,
            {ArticleListPage},
        )

    def test_articlepage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            ArticlePage,
            {},
        )
