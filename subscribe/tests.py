from wagtail.test.utils import WagtailPageTests
from subscribe.models import SubscribePage
from home.models import HomePage


class SubscribePageTests(WagtailPageTests):
    def test_subscribepage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            SubscribePage,
            {HomePage},
        )

    def test_subscribepage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            SubscribePage,
            {},
        )
