from core.models import (
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract,
)
from django.db import models
from streams.blocks import EventsLandingEventCard
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.documents.blocks import DocumentChooserBlock
from django.utils import timezone
from wagtail.search import index
import pytz
import re
import urllib.parse
import json


class EventListPage(BasicPageAbstract, SearchablePageAbstract, Page):
    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['events.EventPage']
    templates = 'events/event_list_page.html'
    featured_events = StreamField(
        [
            ('event', EventsLandingEventCard()),
        ],
        blank=True,
        use_json_field=True,
    )

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.hero_link_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
        FieldPanel('featured_events'),
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields + SearchablePageAbstract.search_fields

    def get_all_events(self):
        from .models import EventPage

        event_pages = EventPage.objects.live().specific().prefetch_related(
            'authors__author', 'topics'
        ).order_by('-publishing_date')

        events_list = []
        for item in event_pages:
            item_dict = {}

            item_dict['title'] = item.feature_title if item.feature_title else item.title
            item_dict['authors'] = [{
                'title': author.author.title,
                'url': author.author.url
            } for author in item.authors.all()]
            item_dict['date'] = item.event_start_time_local.strftime('%A, %B %-d, %Y')
            item_dict['date_singular'] = item.event_start_time_local.strftime('%-d')
            item_dict['month'] = item.event_start_time_local.strftime('%B')
            item_dict['time'] = item.event_start_time_local.strftime('%-I:%M %p')
            item_dict['end_date'] = item.event_end_time_local.strftime('%Y-%m-%d') if item.event_end else ''
            item_dict['end_time'] = item.event_end_time_local.strftime('%-I:%M %p') if item.event_end else ''
            item_dict['event_type'] = item.get_event_type_display()
            item_dict['event_access'] = item.get_event_access_display()
            item_dict['event_format'] = item.event_format_string
            item_dict['is_past'] = item.is_past()
            item_dict['time_zone_label'] = item.time_zone_label
            item_dict['url'] = item.feature_url if item.feature_url else item.url
            item_dict['topics'] = [{
                'title': topic.title,
                'url': topic.url
            } for topic in item.topics_sorted]
            item_dict['registration_url'] = item.registration_url
            item_dict['id'] = item.id
            item_dict['start_utc'] = item.event_start_time_utc.timestamp()
            item_dict['end_utc'] = item.event_end_time_utc.timestamp() if item.event_end else ''

            events_list.append(item_dict)

        def batched(lst, batch_size):
            return [lst[i: i + batch_size] for i in range(0, len(lst), batch_size)]

        batched_list = batched(events_list, 4)
        events_dict = {}
        for batch in range(len(batched_list)):
            events_dict[str(batch)] = list(batched_list[batch])

        return json.dumps({
            'meta': {
                'total_events_count': len(events_list),
                'total_page_count': len(batched_list)},
            'items': events_dict,
        })

    def get_featured_events(self):
        featured_events = [item.value.get('page') for item in self.featured_events]
        featured_events_content = []

        for item in featured_events:
            item_dict = {}

            item_dict['title'] = item.feature_title if item.feature_title else item.title
            item_dict['authors'] = [{
                'title': author.author.title,
                'url': author.author.url
            } for author in item.authors.all()]
            item_dict['date'] = item.event_start_time_local.strftime('%A, %B %-d, %Y')
            item_dict['date_singular'] = item.event_start_time_local.strftime('%-d')
            item_dict['month'] = item.event_start_time_local.strftime('%B')
            item_dict['time'] = item.event_start_time_local.strftime('%-I:%M %p')
            item_dict['end_date'] = item.event_end_time_local.strftime('%Y-%m-%d') if item.event_end else ''
            item_dict['end_time'] = item.event_end_time_local.strftime('%-I:%M %p') if item.event_end else ''
            item_dict['event_type'] = item.get_event_type_display()
            item_dict['event_access'] = item.get_event_access_display()
            item_dict['event_format'] = item.event_format_string
            item_dict['is_past'] = item.is_past()
            item_dict['time_zone_label'] = item.time_zone_label
            item_dict['url'] = item.feature_url if item.feature_url else item.url
            item_dict['topics'] = [{
                'title': topic.title,
                'url': topic.url
            } for topic in item.topics_sorted]
            item_dict['registration_url'] = item.registration_url
            item_dict['id'] = item.id
            item_dict['start_utc'] = item.event_start_time_utc.timestamp()
            item_dict['end_utc'] = item.event_end_time_utc.timestamp() if item.event_end else ''

            item_dict['image_hero_url'] = item.image_hero_url
            item_dict['livestream_url'] = item.livestream_url if item.livestream_url else ''
            if item.multimedia_page:
                if item.multimedia_page.specific.vimeo_url:
                    item_dict['vimeo_url'] = item.multimedia_page.specific.vimeo_url

            featured_events_content.append(item_dict)

        return json.dumps({
            'meta': {
                'total_events_count': len(featured_events_content),
            },
            'items': featured_events_content,
        })

    def get_context(self, request):
        context = super().get_context(request)
        context['all_events'] = self.get_all_events()
        context['featured_events_content'] = self.get_featured_events()
        return context

    class Meta:
        verbose_name = 'Event List Page'


class EventPage(
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    ShareablePageAbstract,
):
    class EventAccessOptions(models.IntegerChoices):
        PRIVATE = (0, 'Private')
        PUBLIC = (1, 'Public')

    class EventFormats(models.TextChoices):
        HYBRID = ('hybrid', 'Hybrid')
        VIRTUAL = ('virtual', 'Virtual')
        IN_PERSON = ('in-person', 'In Person')

    class EventTypes(models.TextChoices):
        CIGI_SPONSORED = ('cigi_sponsored', 'CIGI Sponsored')
        CINEMA_SERIES = ('cinema_series', 'Cinema Series')
        COMMUNITY_EVENT = ('community_event', 'Community Event')
        CONFERENCE = ('conference', 'Conference')
        GLOBAL_POLICY_FORUM = ('global_policy_forum', 'Global Policy Forum')
        NOON_LECTURE_SERIES = ('noon_lecture_series', 'Noon Lecture Series')
        PANEL_DISCUSSION = ('panel_discussion', 'Panel Discussion')
        PUBLICATION_LAUNCH = ('publication_launch', 'Publication Launch')
        ROUNDTABLE = ('roundtable', 'Round Table')
        SEMINAR = ('seminar', 'Seminar')
        SIGNATURE_LECTURE = ('signature_lecture', 'Signature Lecture')
        VIRTUAL_EVENT = ('virtual_event', 'Virtual Event')
        WORKSHOP = ('workshop', 'Workshop')

    class InvitationTypes(models.IntegerChoices):
        RSVP_REQUIRED = (0, 'RSVP Required')
        INVITATION_ONLY = (1, 'Invitation Only')
        NO_RSVP = (2, 'No RSVP Required')

    class EventTimeZones(models.TextChoices):
        HAWAII = ('US/Hawaii', '(UTC–10:00) Hawaiian Time')
        LOS_ANGELES = ('America/Los_Angeles', '(UTC–08:00/09:00) Pacific Time')
        DENVER = ('America/Denver', '(UTC–06:00/07:00) Mountain Time')
        CHICAGO = ('America/Chicago', '(UTC–05:00/06:00) Central Time')
        TORONTO = ('America/Toronto', '(UTC–04:00/05:00) Eastern Time')
        CARACAS = ('America/Caracas', '(UTC–04:30) Venezuela Time')
        HALIFAX = ('America/Halifax', '(UTC–03:00/04:00) Atlantic Time')
        SAO_PAULO = ('America/Sao_Paulo', '(UTC–03:00) E. South America Time')
        CAPE_VERDE = ('Atlantic/Cape_Verde', '(UTC–01:00) Cape Verde Time')
        LONDON = ('Europe/London', '(UTC+00:00/01:00) GMT/BST')
        BERLIN = ('Europe/Berlin', '(UTC+01:00/02:00) Central European Time')
        BEIRUT = ('Asia/Beirut', '(UTC+02:00/03:00) Eastern European Time')
        MOSCOW = ('Europe/Moscow', '(UTC+03:00) Russian Time')
        TEHRAN = ('Asia/Tehran', '(UTC+02:30/03:30) Iran Time')
        DUBAI = ('Asia/Dubai', '(UTC+04:00) Arabian Time')
        KABUL = ('Asia/Kabul', '(UTC+04:30) Afghanistan Time')
        ASHGABAT = ('Asia/Ashgabat', '(UTC+05:00) West Asia Time')
        KOLKATA = ('Asia/Kolkata', '(UTC+05:30) India Time')
        KATHMANDU = ('Asia/Kathmandu', '(UTC+05:45) Nepal Time')
        YANGON = ('Asia/Yangon', '(UTC+06:30) Myanmar Time')
        BANGKOK = ('Asia/Bangkok', '(UTC+07:00) SE Asia Time')
        SHANGHAI = ('Asia/Shanghai', '(UTC+08:00) China Time')
        TOKYO = ('Asia/Tokyo', '(UTC+09:00) Tokyo Time')
        SYDNEY = ('Australia/Sydney', '(UTC+10:00/11:00) AUS Eastern Time')
        AUCKLAND = ('Pacific/Auckland', '(UTC+12:00/13:00) New Zealand Time')

    embed_youtube = models.URLField(blank=True)
    event_access = models.IntegerField(choices=EventAccessOptions.choices, default=EventAccessOptions.PUBLIC, null=True, blank=False)
    event_end = models.DateTimeField(blank=True, null=True)
    event_format = models.CharField(
        blank=False,
        max_length=32,
        null=True,
        choices=EventFormats.choices,
    )
    event_type = models.CharField(
        blank=False,
        max_length=32,
        null=True,
        choices=EventTypes.choices,
    )
    flickr_album_url = models.URLField(blank=True)
    invitation_type = models.IntegerField(choices=InvitationTypes.choices, default=InvitationTypes.RSVP_REQUIRED)
    livestream_url = models.URLField(
        blank=True,
        verbose_name='Livestream URL',
        help_text='The Vimeo URL of the livestream event.',
    )
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
    registration_url = models.URLField(blank=True, max_length=512)
    related_files = StreamField(
        [
            ('file', DocumentChooserBlock()),
        ],
        blank=True,
        use_json_field=True,
    )
    short_description = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'link'],
    )
    time_zone = models.CharField(
        blank=True,
        max_length=64,
        choices=EventTimeZones.choices,
        default=EventTimeZones.TORONTO,
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

    def location_string(self):
        # Show event format if it is not virtual only
        if self.event_format in [self.EventFormats.HYBRID, self.EventFormats.IN_PERSON]:
            location_strings = [
                self.location_address1,
                self.location_address2,
                self.location_city,
                self.location_province,
                self.location_postal_code,
                self.location_country
            ]
            return ', '.join([x for x in location_strings if x])
        return ''

    def location_map_url(self):
        return f'https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(self.location_string())}'

    @property
    def event_format_string(self):
        return self.get_event_format_display()

    @property
    def multimedia_url(self):
        if self.multimedia_page:
            return self.multimedia_page.url
        return ''

    def is_past(self):
        now = timezone.now()
        if self.event_end:
            return self.event_end < now
        else:
            return self.publishing_date < now

    @property
    def event_start_time_utc(self):
        '''
        returns UTC datetime object
        - The datetime value entered in EventPage is currently assumed tzinfo="America/Toronto",
        regardless of the "time_zone" field specified; eg. "07:00:00AM America/Los_Angelos"
        - This is then converted to UTC and stored as "publishing_date"; eg. "11:00:00 (during daylight saving)."
        - So to allow specifying different timezones for the "time_zone" field, we need to first
        convert "publishing_date" from UTC back to "America/Toronto", then replace tzinfo with "time_zone"
        - If in the future, "publishing_date" is fixed to have user-specified timezone instead,
        this conversion and replacement would be unnecessary (and incorrect);
        can pass `return item.publishing_date` instead
        - This applies to item.event_end as well
        '''
        if self.time_zone == '' or not self.time_zone:
            return self.publishing_date
        else:
            default_tz = pytz.timezone('America/Toronto')
            correct_tz = pytz.timezone(self.time_zone) if self.time_zone in pytz.all_timezones else default_tz
            return pytz.utc.normalize(
                correct_tz.localize(
                    self.publishing_date.astimezone(default_tz).replace(tzinfo=None)
                )
            )

    @property
    def event_start_time_local(self):
        timezone = pytz.timezone(self.time_zone) if self.time_zone in pytz.all_timezones else pytz.timezone('America/Toronto')
        return self.event_start_time_utc.astimezone(timezone)

    @property
    def event_end_time_utc(self):
        if self.time_zone == '' or not self.time_zone:
            return self.event_end
        else:
            default_tz = pytz.timezone('America/Toronto')
            correct_tz = pytz.timezone(self.time_zone) if self.time_zone in pytz.all_timezones else default_tz
            return pytz.utc.normalize(
                correct_tz.localize(
                    self.event_end.astimezone(default_tz).replace(tzinfo=None)
                )
            )

    @property
    def event_end_time_local(self):
        timezone = pytz.timezone(self.time_zone) if self.time_zone in pytz.all_timezones else pytz.timezone('America/Toronto')
        return self.event_end_time_utc.astimezone(timezone)

    @property
    def time_zone_label(self):
        # timezone could have been assigned in freeform (previous version), or from a list of options (post change)
        # if it's from a list of options post change:
        if self.time_zone in self.EventTimeZones.values:
            '''
            timezone name set to short code based on self.time_zone value; in case no name is available,
            "%Z" returns offset: (eg "+0430" for Iran Time, together with offset this becomes "+0430 (UTC+0430)");
            use regex matching to remove the short code and only display offset in this case.
            '''
            tz = re.sub(r'[-+]\d{2,4} ',
                        '',
                        f'{self.event_start_time_utc.astimezone(pytz.timezone(self.time_zone)).strftime("%Z")} ')
            offset = self.event_start_time_utc.astimezone(pytz.timezone(self.time_zone)).strftime('%z')
            # return string format: "TZ (OFFSET)"" eg. "EDT (UTC-04:00)"
            label = f'{tz}(UTC{offset[:3].replace("-", "–")}:{offset[3:]})'
        # if it's not assigned: default to eastern
        elif not self.time_zone:
            tz_and_offset = self.event_start_time_utc.astimezone(pytz.timezone('America/Toronto')).strftime('%Z%z')
            label = f'{tz_and_offset[:3]} (UTC{tz_and_offset[3:6].replace("-", "–")}:{tz_and_offset[6:]})'
        # if it was assigned in freeform - preserve
        else:
            label = self.time_zone
        return label

    @property
    def card_url(self):
        return self.feature_url if self.feature_url else self.url

    def get_context(self, request):
        context = super().get_context(request)
        context['location_string'] = self.location_string()
        context['event_format_string'] = self.get_event_format_display()
        context['location_map_url'] = self.location_map_url()
        return context

    content_panels = [
        BasicPageAbstract.title_panel,
        MultiFieldPanel(
            [
                FieldPanel('short_description'),
                FieldPanel('body'),
            ],
            heading='Body',
            classname='collapsible collapsed'
        ),
        BasicPageAbstract.images_panel,
        FieldPanel('publishing_date', heading='Event start'),
        FieldPanel('event_end'),
        FieldPanel('time_zone'),
        MultiFieldPanel(
            [
                FieldPanel('event_format'),
                FieldPanel('event_type'),
                FieldPanel('event_access'),
                FieldPanel('invitation_type'),
                FieldPanel('livestream_url'),
                FieldPanel('website_url'),
                FieldPanel('website_button_text'),
                FieldPanel('registration_url'),
            ],
            heading='Event Details',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                InlinePanel('authors'),
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
                FieldPanel('related_files'),
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
                FieldPanel('issues'),
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

    search_fields = BasicPageAbstract.search_fields \
        + ContentPage.search_fields \
        + [
            index.FilterField('publishing_date'),
            index.FilterField('event_access'),
        ]

    parent_page_types = ['events.EventListPage']
    subpage_types = []
    templates = 'events/event_page.html'

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
