from core.models import HomePage
from wagtail.tests.utils import WagtailPageTests

from .models import NewsletterListPage


class NewsletterListPageTests(WagtailPageTests):
    def test_newsletterlistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            NewsletterListPage,
            {HomePage},
        )

    def test_newsletterlistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            NewsletterListPage,
            {},
        )
