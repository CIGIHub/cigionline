from django.db import models
from multimedia.models import MultimediaPage
from wagtail.admin.panels import FieldPanel, PageChooserPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class PromotionBlock(models.Model):
    class PromotionBlockTypes(models.TextChoices):
        STANDARD = ('standard', 'Standard')
        SOCIAL = ('social', 'Social')
        WIDE = ('wide', 'Wide')
        PODCAST_PLAYER = ('podcast_player', 'Podcast Player')

    name = models.CharField(
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
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Promotion Image',
        help_text='The background image of the promotion block.',
    )
    image_promotion_small = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Promotion Image (Small)',
        help_text='The background image of the promotion block. Only used for wide promotion blocks as a replacement when screen width is small. Ex. Multimedia landing page wide promotion block.',
    )
    podcast_episode = models.ForeignKey(
        'multimedia.MultimediaPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Podcast Episode',
        help_text='The podcast episode that should be displayed on the ad block. Leave empty for the latest episode',
    )
    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('block_type'),
        FieldPanel('link_url'),
        FieldPanel('image_promotion'),
        FieldPanel('image_promotion_small'),
        PageChooserPanel('podcast_episode', ['multimedia.MultimediaPage']),
    ]

    def __str__(self):
        return self.name

    @property
    def episode(self):
        if self.podcast_episode:
            return self.podcast_episode
        return MultimediaPage.objects.live().filter(multimedia_series__title="Big Tech Podcast").order_by("-publishing_date")[0]

    class Meta:
        verbose_name = 'Promotion Block'
