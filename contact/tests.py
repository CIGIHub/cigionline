from home.models import HomePage
from wagtail.test.utils import WagtailPageTests

from .models import ContactPage


class ContactPageTests(WagtailPageTests):
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
