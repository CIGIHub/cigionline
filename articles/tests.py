from core.models import HomePage
from wagtail.tests.utils import WagtailPageTests

from .models import ArticleListPage


class ArticleListPageTests(WagtailPageTests):
    def test_articlelistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            ArticleListPage,
            {HomePage},
        )

    def test_articlelistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            ArticleListPage,
            {},
        )
