from home.models import HomePage
from wagtail.tests.utils import WagtailPageTests

from .models import PromotionBlockListPage, PromotionBlockPage


class PromotionBlockListPageTests(WagtailPageTests):
    def test_promotionblocklistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PromotionBlockListPage,
            {HomePage},
        )

    def test_PromotionBlocklistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PromotionBlockListPage,
            {PromotionBlockPage},
        )


class PromotionBlockPageTests(WagtailPageTests):
    def test_promotionblockpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PromotionBlockPage,
            {PromotionBlockListPage},
        )

    def test_promotionblockpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PromotionBlockPage,
            {},
        )
