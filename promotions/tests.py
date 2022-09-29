from wagtail.test.utils import WagtailPageTests

from .models import PromotionBlock


class PromotionBlockPageTests(WagtailPageTests):
    def test_create_promotion_block(self):
        test_block = PromotionBlock.objects.create(name="test1", block_type=PromotionBlock.PromotionBlockTypes.STANDARD, link_url="https://test.test")
        self.assertTrue(isinstance(test_block, PromotionBlock))
        self.assertEqual(str(test_block), test_block.name)
