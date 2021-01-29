from django.db import models

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel


class PromotionBlock(models.Model):
    class PromotionBlockTypes(models.TextChoices):
        STANDARD = ('standard', 'Standard')
        SOCIAL = ('social', 'Social')
        WIDE = ('wide', 'Wide')

    title = models.CharField(
        blank=False,
        max_length=32
    )
    block_type = models.CharField(
        blank=False,
        max_length=32,
        choices=PromotionBlockTypes.choices,
        default=PromotionBlockTypes.STANDARD
    )
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
        verbose_name='Promotion Image (Small)',
        help_text='The background image of the promotion block. Only used for wide promotion blocks as a replacement when screen width is small. Ex. Multimedia landing page wide promotion block.',
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('block_type'),
        FieldPanel('link_url'),
        ImageChooserPanel('image_promotion'),
    ]

    class Meta:
        verbose_name = 'Promotion Block'
