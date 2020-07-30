from core.models import (
    BasicPageAbstract,
    FeatureablePageAbstract,
    PublishablePageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
)
from django.db import models
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.core.blocks import (
    CharBlock,
    IntegerBlock,
    StructBlock,
    TextBlock,
)
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel


class MultimediaListPage(BasicPageAbstract):
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = []
    templates = 'multimedia/multimedia_list_page.html'

    class Meta:
        verbose_name = 'Multimedia List Page'


class MultimediaPage(
    BasicPageAbstract,
    FeatureablePageAbstract,
    PublishablePageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
):
    multimedia_series = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    multimedia_url = models.URLField(
        blank=True,
        verbose_name='Multimedia URL',
        help_text='The URL of the multimedia source from YouTube or Simplecast.',
    )
    podcast_audio_duration = models.CharField(blank=True, max_length=8)
    podcast_audio_file_size = models.IntegerField(blank=True, null=True)
    podcast_audio_url = models.URLField(blank=True)
    podcast_episode = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Episode Number',
    )
    podcast_season = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Season Number',
    )
    podcast_video_duration = models.CharField(blank=True, max_length=8)
    podcast_video_file_size = models.IntegerField(blank=True, null=True)
    podcast_video_url = models.URLField(blank=True)
    topics = ParentalManyToManyField('research.TopicPage', blank=True)
    video_chapters = StreamField(
        [
            ('video_chapter', StructBlock([
                ('chapter_title', CharBlock(required=True)),
                ('location_time', IntegerBlock(required=True)),
                ('chapter_description', TextBlock(required=False)),
            ])),
        ],
        blank=True,
    )
    youtube_id = models.CharField(
        blank=True,
        max_length=32,
        verbose_name='YouTube ID',
        help_text='Enter just the YouTube ID for this video. This is the series of letters and numbers found either at www.youtube.com/embed/[here], or www.youtube.com/watch?v=[here]. This is used for the video chaptering below.',
    )

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        MultiFieldPanel(
            [
                FieldPanel('publishing_date'),
                FieldPanel('multimedia_url'),
            ],
            heading='General Information',
            classname='collapsible',
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('image_hero'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('youtube_id'),
                StreamFieldPanel('video_chapters'),
            ],
            heading='Video Chapters',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('podcast_season'),
                FieldPanel('podcast_episode'),
                MultiFieldPanel(
                    [
                        FieldPanel('podcast_audio_url'),
                        FieldPanel('podcast_audio_duration'),
                        FieldPanel('podcast_audio_file_size'),
                    ],
                    heading='Audio',
                    classname='collapsible collapsed',
                ),
                MultiFieldPanel(
                    [
                        FieldPanel('podcast_video_url'),
                        FieldPanel('podcast_video_duration'),
                        FieldPanel('podcast_video_file_size'),
                    ],
                    heading='Video',
                    classname='collapsible collapsed',
                ),
            ],
            heading='Podcast Details',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                PageChooserPanel(
                    'multimedia_series',
                    ['multimedia.MultimediaSeriesPage'],
                ),
                FieldPanel('topics'),
            ],
            heading='Related',
            classname='collapsible collapsed',
        ),
    ]

    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
    ]

    settings_panels = Page.settings_panels + [
        ThemeablePageAbstract.theme_panel,
    ]

    parent_page_types = ['multimedia.MultimediaListPage']
    subpage_typse = []
    templates = 'multimedia/multimedia_page.html'

    class Meta:
        verbose_name = 'Multimedia'
        verbose_name_plural = 'Multimedia'


class MultimediaSeriesListPage(Page):
    """
    A singleton page that isn't published, but is the parent to all the
    multimedia series pages at the path /multimedia-series.
    """
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = ['multimedia.MultimediaSeriesPage']
    templates = 'multimedia/multimedia_series_list_page.html'

    class Meta:
        verbose_name = 'Multimedia Series List Page'


class MultimediaSeriesPage(
    BasicPageAbstract,
    FeatureablePageAbstract,
    PublishablePageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
):
    image_banner = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Image',
    )
    image_logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Series Logo',
    )
    image_poster = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Poster Image',
        help_text='A poster image which will be used in the highlights section of the homepage.',
    )
    podcast_apple_url = models.URLField(
        blank=True,
        verbose_name='Apple Podcast URL',
        help_text='Enter the link to the Apple Podcast landing page for this podcast.',
    )
    podcast_google_url = models.URLField(
        blank=True,
        verbose_name='Google Podcast URL',
        help_text='Enter the link to the Google Podcast landing page for the podcast.',
    )
    podcast_spotify_url = models.URLField(
        blank=True,
        verbose_name='Spotify Podcast URL',
        help_text='Enter the link to the Spotify Podcast landing page for the podcast.',
    )
    topics = ParentalManyToManyField('research.TopicPage', blank=True)

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        MultiFieldPanel(
            [
                FieldPanel('publishing_date'),
            ],
            heading='General Information',
            classname='collapsible',
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('image_hero'),
                ImageChooserPanel('image_banner'),
                ImageChooserPanel('image_poster'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('image_logo'),
                FieldPanel('podcast_apple_url'),
                FieldPanel('podcast_spotify_url'),
                FieldPanel('podcast_google_url'),
            ],
            heading='Podcast Details',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('topics'),
            ],
            heading='Related',
            classname='collapsible collapsed',
        ),
    ]

    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
    ]

    settings_panels = Page.settings_panels + [
        ThemeablePageAbstract.theme_panel,
    ]

    parent_page_types = ['core.HomePage', 'multimedia.MultimediaSeriesListPage']
    subpage_types = []
    templates = 'multimedia/multimedia_series_page.html'

    class Meta:
        verbose_name = 'Multimedia Series'
        verbose_name_plural = 'Multimedia Series'
