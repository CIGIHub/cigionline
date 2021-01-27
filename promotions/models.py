from wagtail.core.models import Page

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel


class PromotionBlockListPage(Page):
    """Promotion Block list page"""

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['promotions.PromotionBlockPage']

    class Meta:
        verbose_name = 'Promotion List Page'


class PromotionBlockPage(Page):
    panels = [
        FieldPanel('link_url'),
        ImageChooserPanel('image_promotion'),
        ImageChooserPanel('image_promotion_small'),
    ]

    class Meta:
        verbose_name = 'Promotion Block'
