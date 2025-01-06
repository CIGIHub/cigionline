from home.models import HomePage, Think7HomePage
from wagtail.test.utils import WagtailPageTestCase

from .models import ContactPage


class ContactPageTests(WagtailPageTestCase):
    def test_contactpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            ContactPage,
            {HomePage, Think7HomePage},
        )

    def test_contactpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            ContactPage,
            {},
        )
