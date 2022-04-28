from django.core.cache import cache
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    InlinePanel,
    MultiFieldPanel,
    FieldPanel
)
from wagtail.core.models import Page
from wagtail.core.models import Orderable


class FeaturesListPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['features.HomePageFeaturedPromotionsPage']
    max_count = 1

    class Meta:
        verbose_name = 'Feature List Page'


class HomePageFeaturedPromotionsPage(Page):
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                InlinePanel(
                    'promotion_blocks',
                    max_num=4,
                    min_num=0,
                    label='Promotion Block',
                ),
            ],
            heading='Promotion Blocks',
            classname='collapsible',
        ),
    ]

    parent_page_types = ['features.FeaturesListPage']
    subpage_types = []
    max_count = 1

    class Meta:
        verbose_name = 'Home Page Featured Promotions Page'


class FeaturesPagePromotionBlocks(Orderable):
    features_page = ParentalKey(
        'features.HomePageFeaturedPromotionsPage',
        related_name='promotion_blocks',
    )
    promotion_block = models.ForeignKey(
        'promotions.PromotionBlock',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Promotion Block',
    )

    panels = [
        FieldPanel(
            'promotion_block',
            ['promotions.PromotionBlock'],
        ),
    ]
