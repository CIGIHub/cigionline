from .forms import EventSubmissionForm
from core.models import (
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract
)
from django.db import models
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.utils import timezone
from modelcluster.fields import ParentalKey
from streams.blocks import AbstractSubmissionBlock
from uploads.models import DocumentUpload
from utils.email_utils import send_email_digital_finance, extract_errors_as_string, send_email_digifincon_debug
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page, Collection
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.documents.models import Document
from wagtail.search import index
import pytz
import re
import urllib.parse
import traceback
import logging


class EventListPage(BasicPageAbstract, SearchablePageAbstract, Page):
    max_count = 2
    parent_page_types = ['home.HomePage', 'home.Think7HomePage']
    subpage_types = ['events.EventPage']
    templates = 'events/event_list_page.html'

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.hero_link_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
        MultiFieldPanel(
            [
                InlinePanel(
                    'featured_events',
                    max_num=6,
                    min_num=0,
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

    search_fields = Page.search_fields + BasicPageAbstract.search_fields + SearchablePageAbstract.search_fields

    def get_featured_events(self):
        featured_event_ids = self.featured_events.order_by('sort_order').values_list('event_page', flat=True)[:6]
        pages = Page.objects.specific().prefetch_related(
            'topics',
        ).in_bulk(featured_event_ids)
        return [pages[x] for x in featured_event_ids]

    def get_featured_events_preview(self):
        featured_events = self.featured_events.order_by('sort_order')
        featured_event_ids = [x.event_page.id for x in featured_events]
        pages = Page.objects.specific().prefetch_related(
            'topics',
        ).in_bulk(featured_event_ids)
        return [pages[x] for x in featured_event_ids]

    def get_context(self, request):
        context = super().get_context(request)
        if hasattr(context['request'], 'is_preview'):
            if context['request'].is_preview:
                context['featured_events'] = self.get_featured_events_preview()
            else:
                context['featured_events'] = self.get_featured_events()
        else:
            context['featured_events'] = self.get_featured_events()
        return context

    def get_template(self, request, *args, **kwargs):
        if self.get_site().site_name == 'Think 7 Canada':
            return 'think7/event_list_page.html'
        return super().get_template(request, *args, **kwargs)

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
    ThemeablePageAbstract,
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

    body = StreamField(
        BasicPageAbstract.body_default_blocks + [
            ('abstract_submission_block', AbstractSubmissionBlock()),
        ],
        blank=True,
    )
    embed_youtube = models.URLField(blank=True)
    event_agenda = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Event agenda',
    )
    event_access = models.IntegerField(choices=EventAccessOptions.choices, default=EventAccessOptions.PUBLIC, null=True, blank=True)
    event_end = models.DateTimeField(blank=True, null=True)
    event_format = models.CharField(
        blank=True,
        max_length=32,
        null=True,
        choices=EventFormats.choices,
    )
    event_type = models.CharField(
        blank=True,
        max_length=32,
        null=True,
        choices=EventTypes.choices,
    )
    email_recipient = models.EmailField(
        blank=True,
        null=True,
        help_text='Email address to send notifications to when a file is uploaded via submission form.',
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
    registration_url = models.URLField(blank=True, max_length=512)
    registration_text = models.CharField(blank=True, max_length=64)
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
    website_url = models.URLField(blank=True, null=True, max_length=512)

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
            correct_tz = pytz.timezone(self.time_zone)
            return pytz.utc.normalize(
                correct_tz.localize(
                    self.publishing_date.astimezone(default_tz).replace(tzinfo=None)
                )
            )

    @property
    def event_end_time_utc(self):
        if self.time_zone == '' or not self.time_zone:
            return self.event_end
        else:
            default_tz = pytz.timezone('America/Toronto')
            correct_tz = pytz.timezone(self.time_zone)
            return pytz.utc.normalize(
                correct_tz.localize(
                    self.event_end.astimezone(default_tz).replace(tzinfo=None)
                )
            )

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

    def get_context(self, request):
        context = super().get_context(request)
        context['location_string'] = self.location_string()
        context['event_format_string'] = self.get_event_format_display()
        context['location_map_url'] = self.location_map_url()
        return context

    def get_template(self, request, *args, **kwargs):
        standard_template = super(EventPage, self).get_template(request, *args, **kwargs)

        if self.get_site().site_name == 'Think 7 Canada':
            return 'think7/event_page.html'

        if self.theme:
            return f'themes/{self.get_theme_dir()}/event_page.html'
        return standard_template

    def serve(self, request):
        get_token(request)
        form = EventSubmissionForm()
        email_recipient = ''

        if self.theme and self.theme.name == 'Digital Finance':
            email_recipient = 'digitalfinanceinquiries@cigionline.org'
        if self.email_recipient:
            email_recipient = self.email_recipient

        if self.theme:
            template = f'themes/{self.get_theme_dir()}/event_page.html'
        else:
            template = 'events/event_page.html'

        if email_recipient and request.method == "POST":
            form = EventSubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = form.cleaned_data['file']
                email = form.cleaned_data['email']
                valid_extensions = ['.pdf', '.doc', '.docx']
                file_extension = uploaded_file.name.lower().split('.')[-1]

                if f'.{file_extension}' in valid_extensions:
                    if self.theme.name == 'Digital Finance':
                        collection = Collection.objects.get(name='Digital Finance Conference Abstracts')
                    else:
                        collection = Collection.objects.get(
                            name='Event submissions',
                        )

                    try:
                        document = Document.objects.create(
                            title=uploaded_file.name,
                            file=uploaded_file,
                            collection=collection,
                        )
                        DocumentUpload.objects.create(
                            document=document, email=email
                        )
                        if email_recipient:
                            try:
                                send_email_digital_finance(
                                    recipient=email_recipient,
                                    subject='Digital Finance Abstract Uploaded Successfully',
                                    body=f'File "{uploaded_file.name}" was uploaded by {email}.\n\nYou can download it from: {request.build_absolute_uri(document.file.url)}\n\n'
                                )
                                send_email_digital_finance(
                                    recipient=email,
                                    subject='Abstract Submission Upload Successful',
                                    body=f'Your file "{uploaded_file.name}" was uploaded successfully. Thank you for your submission.',
                                )
                            except Exception as e:
                                print(str(e))
                        return JsonResponse(
                            {
                                'status': 'success',
                                'message': 'File uploaded successfully!',
                            }
                        )

                    except Exception as e:
                        logging.error("Exception during event form submission", exc_info=True)
                        error_trace = traceback.format_exc()
                        print(str(e))
                        send_email_digifincon_debug(
                            recipient='jxu@cigionline.org',
                            subject='File Upload Failed',
                            body=f"""
                                    An error occurred during abstract submission:

                                    Error: {str(e)}

                                    Traceback:
                                    {error_trace}
                                """,
                        )

                        if email_recipient:
                            send_email_digital_finance(
                                recipient=email_recipient,
                                subject='File Upload Failed',
                                body=f'File upload failed for {email}. Error: {str(e)}',
                            )
                        return JsonResponse(
                            {
                                'status': 'error',
                                'message': f'Failed to save file: {str(e)}',
                            }
                        )
                else:
                    if email_recipient:
                        send_email_digital_finance(
                            recipient=email_recipient,
                            subject='File Upload Failed',
                            body=f'File upload failed for {email}. Invalid file type.',
                        )
                return JsonResponse(
                    {
                        'status': 'error',
                        'message': 'Invalid file type. Only .pdf, .doc, and .docx files are allowed.',
                    }
                )
            else:
                error_message = " ".join(extract_errors_as_string(form.errors))

                if email_recipient:
                    send_email_digital_finance(
                        recipient=email_recipient,
                        subject='Form Submission Failed',
                        body=f'Form submission failed for {form.cleaned_data.get('email', 'Unknown email')}. Invalid data. {error_message}',
                    )

                return JsonResponse(
                    {'status': 'error', 'message': f'Invalid form submission. {error_message}'}
                )

        return render(request, template, {
            "page": self,
            "self": self,
            "form": form,
        })

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
                FieldPanel('website_url'),
                FieldPanel('website_button_text'),
                FieldPanel('registration_url'),
                FieldPanel('registration_text'),
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
                FieldPanel('event_agenda'),
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
                FieldPanel('countries'),
                PageChooserPanel(
                    'multimedia_page',
                    ['multimedia.MultimediaPage'],
                ),
            ],
            heading='Related',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('email_recipient'),
            ],
            heading='Submission Form',
            classname='collapsible collapsed',
        ),
    ]
    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
        SearchablePageAbstract.search_panel,
    ]
    settings_panels = Page.settings_panels + [
        ThemeablePageAbstract.theme_panel,
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
