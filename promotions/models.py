from django.db import models
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
    link_url = models.CharField(
        blank=True,
        max_length=512,
        help_text='An external URL (https://...) or an internal URL (/interactives/2019annualreport/).',
    )
    image_promotion = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Promotion Image',
        help_text='The background image of the promotion block.',
    )
    image_promotion_small = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Promotion Image',
        help_text='The background image of the promotion block. Only used for wide promotion blocks as a replacement when screen width is small. Ex. Multimedia landing page wide promotion block.',
    )

    content_panels = [
        FieldPanel('link_url'),
        ImageChooserPanel('image_promotion'),
        ImageChooserPanel('image_promotion_small'),
    ]

    class Meta:
        verbose_name = 'Promotion Block'
