from home.models import HomePage
from wagtail.test.utils import WagtailPageTestCase

from .models import NewsletterListPage, NewsletterPage


class NewsletterListPageTests(WagtailPageTestCase):
    def test_newsletterlistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            NewsletterListPage,
            {HomePage},
        )

    def test_newsletterlistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            NewsletterListPage,
            {NewsletterPage},
        )


class NewsletterPageTetss(WagtailPageTestCase):
    def test_newsletterpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            NewsletterPage,
            {NewsletterListPage},
        )

    def test_newsletterpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            NewsletterPage,
            {},
        )
