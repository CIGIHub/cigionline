from core.models import (
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract,
)
from django.db import models
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.core.blocks import CharBlock, PageChooserBlock
from wagtail.core.fields import StreamField
from wagtail.core.models import Orderable, Page
from wagtail.documents.blocks import DocumentChooserBlock
from streams.blocks import ExternalSpeakersBlock, SpeakersBlock


class EventListPage(BasicPageAbstract, Page):
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = ['events.EventPage']
    templates = 'events/event_list_page.html'

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
        MultiFieldPanel(
            [
                InlinePanel(
                    'featured_events',
                    max_num=6,
                    min_num=6,
                    label='Event',
                ),
            ],
            heading='Featured Events',
            classname='collapsible collapsed',
        ),
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    class Meta:
        verbose_name = 'Event List Page'


class EventListPageFeaturedEvent(Orderable):
    event_list_page = ParentalKey(
        'events.EventListPage',
        related_name='featured_events',
    )
    event_page = models.ForeignKey(
        'wagtailcore.Page',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Event',
    )

    panels = [
        PageChooserPanel(
            'event_page',
            ['events.EventPage'],
        ),
    ]


class EventPage(
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    ShareablePageAbstract,
):
    class EventAccessOptions(models.IntegerChoices):
        PRIVATE = (0, 'Private')
        PUBLIC = (1, 'Public')

    class EventTypes(models.TextChoices):
        CIGI_SPONSORED = ('cigi_sponsored', 'CIGI Sponsored')
        CINEMA_SERIES = ('cinema_series', 'Cinema Series')
        COMMUNITY_EVENT = ('community_event', 'Community Event')
        CONFERENCE = ('conference', 'Conference')
        GLOBAL_POLICY_FORUM = ('global_policy_forum', 'Global Policy Forum')
        NOON_LECTURE_SERIES = ('noon_lecture_series', 'Noon Lecture Series')
        PANEL_DISCUSSION = ('panel_discussion', 'Panel Discussion')
        PUBLICATION_LAUNCH = ('publication_launch', 'Publication Launch')
        ROUNDTABLE = ('roundtable', 'Roundtable')
        SEMINAR = ('seminar', 'Seminar')
        SIGNATURE_LECTURE = ('signature_lecture', 'Signature Lecture')
        VIRTUAL_EVENT = ('virtual_event', 'Virtual Event')
        WORKSHOP = ('workshop', 'Workshop')

    class InvitationTypes(models.IntegerChoices):
        RSVP_REQUIRED = (0, 'RSVP Required')
        INVITATION_ONLY = (1, 'Invitation Only')
        NO_RSVP = (2, 'No RSVP Required')

    embed_youtube = models.URLField(blank=True)
    event_access = models.IntegerField(choices=EventAccessOptions.choices, default=EventAccessOptions.PUBLIC, null=True, blank=False)
    event_end = models.DateTimeField(blank=True, null=True)
    event_type = models.CharField(
        blank=False,
        max_length=32,
        null=True,
        choices=EventTypes.choices,
    )
    flickr_album_url = models.URLField(blank=True)
    invitation_type = models.IntegerField(choices=InvitationTypes.choices, default=InvitationTypes.RSVP_REQUIRED)
    location_address1 = models.CharField(blank=True, max_length=255, verbose_name='Address (Line 1)')
    location_address2 = models.CharField(blank=True, max_length=255, verbose_name='Address (Line 2)')
    location_city = models.CharField(blank=True, max_length=255, verbose_name='City')
    location_country = models.CharField(blank=True, max_length=255, verbose_name='Country')
    location_name = models.CharField(blank=True, max_length=255)
    location_postal_code = models.CharField(blank=True, max_length=32, verbose_name='Postal Code')
    location_province = models.CharField(blank=True, max_length=255, verbose_name='Province/State')
    multimedia_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Multimedia',
    )
    projects = ParentalManyToManyField('research.ProjectPage', blank=True)
    registration_url = models.URLField(blank=True, max_length=512)
    related_files = StreamField(
        [
            ('file', DocumentChooserBlock()),
        ],
        blank=True,
    )
    speakers = StreamField(
        [
            ('speaker', SpeakersBlock(required=True, page_type='people.PersonPage')),
            ('external_speaker', ExternalSpeakersBlock()),
        ],
        blank=True,
    )
    twitter_hashtag = models.CharField(blank=True, max_length=64)
    website_button_text = models.CharField(
        blank=True,
        max_length=64,
        help_text='Override the button text for the event website. If empty, the button will read "Event Website".'
    )
    website_url = models.URLField(blank=True, max_length=512)

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
        FieldPanel('publishing_date', heading='Event start'),
        FieldPanel('event_end'),
        MultiFieldPanel(
            [
                FieldPanel('event_type'),
                FieldPanel('event_access'),
                FieldPanel('invitation_type'),
                FieldPanel('website_url'),
                FieldPanel('website_button_text'),
                FieldPanel('registration_url'),
            ],
            heading='Event Details',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('speakers'),
            ],
            heading='Speakers',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('location_name'),
                FieldPanel('location_address1'),
                FieldPanel('location_address2'),
                FieldPanel('location_city'),
                FieldPanel('location_province'),
                FieldPanel('location_postal_code'),
                FieldPanel('location_country'),
            ],
            heading='Location',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('embed_youtube'),
                StreamFieldPanel('related_files'),
            ],
            heading='Media',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('twitter_hashtag'),
                FieldPanel('flickr_album_url'),
            ],
            heading='Event Social Media',
            classname='collapsible collapsed',
        ),
        ContentPage.recommended_panel,
        MultiFieldPanel(
            [
                FieldPanel('topics'),
                FieldPanel('projects'),
                PageChooserPanel(
                    'multimedia_page',
                    ['multimedia.MultimediaPage'],
                ),
            ],
            heading='Related',
            classname='collapsible collapsed',
        ),
    ]
    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
        SearchablePageAbstract.search_panel,
    ]

    parent_page_types = ['events.EventListPage']
    subpage_types = []
    templates = 'events/event_page.html'

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
