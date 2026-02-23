from home.models import HomePage
from wagtail.test.utils import WagtailPageTestCase

from .models import PolicyPopupGroupPage


class PolicyPopupGroupPageTests(WagtailPageTestCase):
    def test_policy_popup_group_page_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PolicyPopupGroupPage,
            {HomePage},
        )

    def test_policy_popup_group_page_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PolicyPopupGroupPage,
            {},
        )
