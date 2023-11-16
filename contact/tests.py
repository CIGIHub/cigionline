from home.models import HomePage
from wagtail.test.utils import WagtailPageTestCase

from .models import ContactPage


class ContactPageTests(WagtailPageTestCase):
    def test_contactpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            ContactPage,
            {HomePage},
        )

    def test_contactpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            ContactPage,
            {},
        )
