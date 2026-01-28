from .forms_admin import EventPageAdminForm
from core.models import (
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract
)
from django.contrib import messages
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from streams.blocks import AbstractSubmissionBlock
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    HelpPanel,
)
from wagtail.admin.panels import TabbedInterface, ObjectList
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail import blocks
from wagtail.contrib.forms.models import AbstractFormField
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.images.blocks import ImageChooserBlock
import pytz
import re
import urllib.parse
import uuid


def _split_slugs(s: str):
    return [x.strip() for x in (s or "").split(",") if x.strip()]


def _match(rule: str, slugs: list[str], current_slug: str) -> bool:
    S = set(slugs)
    if rule == "all":
        return True
    if rule == "only":
        return current_slug in S
    if rule == "except":
        return current_slug not in S
    return True


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
    RoutablePageMixin,
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

    base_form_class = EventPageAdminForm

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
    registration_image_banner = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Image',
        help_text='A banner image to be displayed as background of the hero section.',
    )
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

    # Registration related fields
    registration_open = models.BooleanField(default=False)
    is_private_registration = models.BooleanField(
        default=False, help_text="Require invite token or private link to register."
    )
    confirmation_template = models.ForeignKey(
        'events.EmailTemplate', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    waitlist_template = models.ForeignKey(
        'events.EmailTemplate', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    reminder_template = models.ForeignKey(
        'events.EmailTemplate', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    registration_form_template = models.ForeignKey(
        "events.RegistrationFormTemplate",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Choose a reusable set of registration fields."
    )

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

    @property
    def total_confirmed(self):
        return self.registrants.filter(status=Registrant.Status.CONFIRMED).count()

    @property
    def register_url(self):
        return self.url + "register/"

    # ---------- ROUTES ----------

    @route(r"^register/$")
    def register_entry(self, request, *args, **kwargs):
        """
        Landing step. Validates invite token (if required) and shows
        allowed RegistrationType choices OR skips straight to form
        if only one type is available.
        """
        invite = self._get_invite_from_request(request)

        if self.is_private_registration:
            if not invite or not invite.is_valid():
                return self.render(request, context_overrides={
                    "registration_error": "Private registration. Please use your invite link."
                })
            types_qs = self.registration_types.all()
            rule = invite.allowed_rule
            if rule == "only":
                allowed = set(_split_slugs(invite.allowed_type_slugs))
                types_qs = types_qs.filter(slug__in=allowed)
            elif rule == "except":
                blocked = set(_split_slugs(invite.allowed_type_slugs))
                if blocked:
                    types_qs = types_qs.exclude(slug__in=blocked)
        else:
            types_qs = self.registration_types.filter(is_public=True)

        types = list(types_qs.order_by("sort_order"))
        if not types:
            return self.render(
                request,
                template="events/registration_no_types.html",
                context_overrides={"event": self},
            )

        if len(types) == 1:
            base = self.get_url(request=request) or ("/" + self.url_path.lstrip("/"))
            return redirect(f"{base}register/{types[0].slug}/")

        return self.render(
            request,
            template="events/registration_type_select.html",
            context_overrides={"event": self, "types": types, "invite": invite},
        )

    @route(r"^register/result/$")
    def register_result(self, request, *args, **kwargs):
        from .models import Registrant
        status = request.GET.get("s")
        rid = request.GET.get("rid")
        registrant = None
        if rid and status in {"ok", "wait"}:
            registrant = (
                Registrant.objects.select_related("registration_type")
                .filter(pk=rid, event=self).first()
            )
        return self.render(
            request,
            template="events/registration_result.html",
            context_overrides={"event": self, "status": status, "registrant": registrant},
        )

    @route(r"^register/(?P<type_slug>[-\w]+)/$")
    def register_form(self, request, type_slug: str, *args, **kwargs):
        from .forms import build_dynamic_form
        from .utils import save_registrant_from_form
        from .emailing import send_confirmation_email

        if not self.registration_open:
            return self.render(
                request,
                template="events/registration_no_types.html",
                context_overrides={"event": self},
            )

        try:
            reg_type = self.registration_types.get(slug=type_slug)
        except RegistrationType.DoesNotExist:
            return self.render(
                request, template="events/registration_no_types.html", context_overrides={"event": self}
            )

        invite = self._get_invite_from_request(request)
        if self.is_private_registration:
            if not invite or not invite.is_valid():
                return self.render(
                    request,
                    template="events/registration_no_types.html",
                    context_overrides={"event": self},
                )
            if not invite.allows_type_slug(reg_type.slug):
                return self.render(
                    request,
                    template="events/registration_no_types.html",
                    context_overrides={"event": self},
                )

        form_class = build_dynamic_form(self, reg_type, invite)

        if request.method == "POST":
            if request.POST.get("website"):
                base = self.get_url(request=request) or ("/" + self.url_path.lstrip("/"))
                return redirect(f"{base}register/result/?s=bot")

            form = form_class(request.POST, request.FILES)
            if form.is_valid():
                registrant = save_registrant_from_form(self, reg_type, form, invite)

                # Atomically burn invite usage if present
                if invite:
                    Invite.objects.filter(
                        pk=invite.pk, used_count__lt=models.F("max_uses")
                    ).update(used_count=models.F("used_count") + 1)

                confirmed = registrant.confirm_with_capacity()
                send_confirmation_email(registrant, confirmed)

                base = self.get_url(request=request) or ("/" + self.url_path.lstrip("/"))
                s = "ok" if confirmed else "wait"
                return redirect(f"{base}register/result/?s={s}&rid={registrant.pk}")
            else:
                for field, errs in form.errors.items():
                    label = form.fields.get(field).label if field in form.fields else field
                    for e in errs:
                        messages.error(request, f"{label}: {e}" if label else str(e))

                base = self.get_url(request=request) or ("/" + self.url_path.lstrip("/"))
                return self.render(
                    request,
                    template="events/registration_form.html",
                    context_overrides={"event": self, "reg_type": reg_type, "form": form, "invite": invite},
                )
        else:
            form = form_class()

        return self.render(
            request,
            template="events/registration_form.html",
            context_overrides={"event": self, "reg_type": reg_type, "form": form, "invite": invite},
        )

    def _get_invite_from_request(self, request):
        token = request.GET.get("invite")
        if token:
            inv = Invite.objects.filter(event=self, token=token).first()
            if inv:
                request.session[f"invite:{self.id}"] = token
                return inv
        token = request.session.get(f"invite:{self.id}")
        if token:
            return Invite.objects.filter(event=self, token=token).first()
        return None

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
    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList([
            MultiFieldPanel(
                [
                    FieldPanel('registration_open'),
                    FieldPanel('is_private_registration'),
                    FieldPanel('registration_image_banner'),
                ],
                heading='General Settings',
                classname='collapsible collapsed',
            ),
            MultiFieldPanel(
                [
                    FieldPanel('confirmation_template'),
                    FieldPanel('waitlist_template'),
                ],
                heading='Email Templates',
                classname='collapsible collapsed',
            ),
            MultiFieldPanel(
                [
                    InlinePanel('registration_types', label='Registration Types'),
                ],
                heading='Registration Types',
                classname='collapsible collapsed',
            ),
            MultiFieldPanel(
                [
                    FieldPanel("registration_form_template"),
                ],
                heading='Registration Form Template',
                classname='collapsible collapsed',
            ),
            MultiFieldPanel(
                [InlinePanel("invites", label="Invites")],
                heading="Invites",
                classname="collapsible collapsed",
            ),
        ], heading='Registration'),
        ObjectList(promote_panels, heading='Promote'),
        ObjectList(settings_panels, heading='Settings', classname='settings'),
    ])

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


class RegistrationType(Orderable):
    event = ParentalKey(
        "events.EventPage", related_name="registration_types", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    custom_confirmation_text = RichTextField(blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("capacity"),
        FieldPanel("is_public"),
        FieldPanel("custom_confirmation_text"),
    ]

    def __str__(self) -> str:
        return f"{self.name}" + (f" (cap {self.capacity})" if self.capacity is not None else "")


class RegistrationFormField(AbstractFormField):
    FIELD_CHOICES = (
        ("singleline", _("Single line text")),
        ("multiline", _("Multi-line text")),
        ("email", _("Email")),
        ("number", _("Number")),
        ("url", _("URL")),
        ("checkbox", _("Checkbox")),
        ("checkboxes", _("Checkboxes")),
        ("dropdown", _("Drop down")),
        ("multiselect", _("Multiple select")),
        ("radio", _("Radio buttons")),
        ("date", _("Date")),
        ("datetime", _("Date/time")),
        ("hidden", _("Hidden field")),
        ("file", _("File upload")),
        ("conditional_text", _("Conditional text (checkbox + details)")),
        ("conditional_dropdown_other", _("Conditional dropdown (Other + textbox)")),
    )
    field_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    template = ParentalKey(
        "events.RegistrationFormTemplate",
        related_name="fields",
        on_delete=models.CASCADE,
    )

    file_allowed_types = models.CharField(
        max_length=255, blank=True,
        help_text="Allowed extensions (comma-separated), e.g. pdf,docx,png"
    )
    file_max_mb = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Max file size (MB). Leave blank for no limit."
    )

    field_type = models.CharField(
        max_length=32,
        choices=FIELD_CHOICES,
        default="singleline",
    )

    class Rule(models.TextChoices):
        ALL = "all", "All types"
        ONLY = "only", "Only these types"
        EXCEPT = "except", "All except these types"

    visible_rule = models.CharField(max_length=10, choices=Rule.choices, default=Rule.ALL)
    visible_type_slugs = models.TextField(blank=True, help_text="Comma-separated type slugs (e.g., vip,speaker)")

    required_rule = models.CharField(max_length=10, choices=Rule.choices, default=Rule.ALL)
    required_type_slugs = models.TextField(blank=True, help_text="Comma-separated type slugs")

    conditional_label = models.CharField(
        max_length=255,
        blank=True,
        help_text="Label shown for the checkbox. If blank, uses the field's main label.",
    )
    conditional_details_label = models.CharField(
        max_length=255,
        blank=True,
        help_text="Label for the details textbox (shown only when checked).",
    )
    conditional_details_help_text = models.TextField(
        blank=True,
        help_text="Help text shown under the details textbox.",
    )
    conditional_details_required = models.BooleanField(
        default=True,
        help_text="Require details textbox when checkbox is checked.",
    )
    conditional_other_value = models.CharField(
        max_length=120,
        blank=True,
        help_text='Which dropdown value triggers the textbox (default: "Other").',
    )
    conditional_other_label = models.CharField(
        max_length=255,
        blank=True,
        help_text="Label for the textbox shown when 'Other' is selected.",
    )
    conditional_other_help_text = models.TextField(
        blank=True,
        help_text="Help text for the 'Other' textbox.",
    )
    conditional_other_required = models.BooleanField(
        default=True,
        help_text="Require textbox when 'Other' is selected.",
    )

    panels = AbstractFormField.panels + [
        MultiFieldPanel(
            [
                FieldPanel("visible_rule"),
                FieldPanel("visible_type_slugs"),
            ],
            heading="Visibility rules",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("required_rule"),
                FieldPanel("required_type_slugs"),
            ],
            heading="Requiredness rules",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("conditional_label"),
                FieldPanel("conditional_details_label"),
                FieldPanel("conditional_details_help_text"),
                FieldPanel("conditional_details_required"),
            ],
            heading="Conditional form settings",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("conditional_other_value"),
                FieldPanel("conditional_other_label"),
                FieldPanel("conditional_other_help_text"),
                FieldPanel("conditional_other_required"),
            ],
            heading="Conditional 'Other' settings",
            classname="collapsible collapsed",
        )
    ]


class Invite(Orderable):
    event = ParentalKey("events.EventPage", related_name="invites", on_delete=models.CASCADE)

    email = models.EmailField(blank=True)
    max_uses = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Rule(models.TextChoices):
        ALL = "all", "All"
        ONLY = "only", "Only these"
    allowed_rule = models.CharField(max_length=10, choices=Rule.choices, default=Rule.ALL)
    allowed_type_slugs = models.TextField(blank=True, help_text="Example: vip,speaker")

    token = models.CharField(max_length=64, unique=True, db_index=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    panels = [
        FieldPanel("email"),
        FieldPanel("allowed_rule"),
        FieldPanel("allowed_type_slugs"),
        FieldPanel("max_uses"),
        FieldPanel("expires_at"),
        FieldPanel("used_count", read_only=True),
        FieldPanel("token", read_only=True),
        HelpPanel(template="events/includes/invite_link_help_panel.html", heading="Invite link"),
    ]

    def save(self, *args, **kwargs):
        if not self.token:
            import secrets
            self.token = secrets.token_urlsafe(24)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invite for {self.event.title} ({self.email or self.token})"

    def is_valid(self) -> bool:
        """Still usable? (not expired, under max uses)"""
        if self.expires_at and timezone.now() >= self.expires_at:
            print("expired")
            return False
        if self.max_uses is not None and self.used_count >= self.max_uses:
            print("maxed out")
            return False
        return True

    def _allowed_set(self):
        return {s.strip() for s in (self.allowed_type_slugs or "").split(",") if s.strip()}

    def allows_type_slug(self, slug: str) -> bool:
        s = slug.strip()
        if self.allowed_rule == self.Rule.ONLY:
            return s in self._allowed_set()
        if self.allowed_rule == self.Rule.EXCEPT:
            return s not in self._allowed_set()
        return True


class Registrant(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        WAITLISTED = "waitlisted", "Waitlisted"
        CANCELLED = "cancelled", "Cancelled"

    event = models.ForeignKey("events.EventPage", on_delete=models.CASCADE, related_name="registrants")
    registration_type = models.ForeignKey(RegistrationType, on_delete=models.PROTECT, related_name="registrants")
    email = models.EmailField()
    first_name = models.CharField(max_length=120, blank=True)
    last_name = models.CharField(max_length=120, blank=True)

    # Store dynamic answers + uploaded docs metadata
    answers = models.JSONField(default=dict, blank=True)
    uploaded_document_ids = models.JSONField(default=list, blank=True)

    invite = models.ForeignKey(Invite, null=True, blank=True, on_delete=models.SET_NULL, related_name="registrants")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.email} @ {self.event.title} ({self.registration_type.name})"

    def confirm_with_capacity(self) -> bool:
        """
        Try to confirm respecting capacity. If capacity is None, always confirm.
        Uses an atomic update on the type to avoid race conditions.
        """
        if self.registration_type.capacity is None:
            self.status = Registrant.Status.CONFIRMED
            self.save(update_fields=["status"])
            return True

        with transaction.atomic():
            RegistrationType.objects.select_for_update().get(pk=self.registration_type_id)
            confirmed_count = Registrant.objects.filter(
                registration_type_id=self.registration_type_id,
                status=Registrant.Status.CONFIRMED
            ).count()

            if confirmed_count < (self.registration_type.capacity or 0):
                self.status = Registrant.Status.CONFIRMED
                self.save(update_fields=["status"])
                return True

            self.status = Registrant.Status.WAITLISTED
            self.save(update_fields=["status"])
            return False


@register_snippet
class EmailTemplate(models.Model):
    title = models.CharField(max_length=120)
    subject = models.CharField(max_length=200)
    # Body supports rich content + optional placeholder merge fields
    body = StreamField(
        [
            ("heading", blocks.StructBlock(
                [
                    ("text", blocks.CharBlock(required=True, max_length=200)),
                    (
                        "level",
                        blocks.ChoiceBlock(
                            choices=[("h1", "H1"), ("h2", "H2"), ("h3", "H3")],
                            default="h2",
                            required=True,
                        ),
                    ),
                ],
                icon="title",
                label="Heading",
            )),
            (
                "paragraph",
                blocks.RichTextBlock(features=["bold", "italic", "link", "ul", "ol"]),
            ),
            (
                "button",
                blocks.StructBlock(
                    [
                        ("text", blocks.CharBlock(required=True, max_length=64)),
                        ("url", blocks.URLBlock(required=True)),
                    ],
                    icon="link",
                    label="Button",
                ),
            ),
            (
                "image",
                blocks.StructBlock(
                    [
                        ("image", ImageChooserBlock(required=False)),
                        ("image_url", blocks.URLBlock(required=False, help_text="Use if you can't choose an image.")),
                        ("alt", blocks.CharBlock(required=False, max_length=200)),
                        (
                            "alignment",
                            blocks.ChoiceBlock(
                                choices=[("left", "Left"), ("center", "Center"), ("right", "Right")],
                                default="center",
                                required=True,
                            ),
                        ),
                        ("max_width", blocks.IntegerBlock(required=False, help_text="In pixels (e.g., 560).")),
                        ("link", blocks.URLBlock(required=False)),
                    ],
                    icon="image",
                    label="Image",
                ),
            ),
            ("divider", blocks.StaticBlock(icon="horizontalrule", label="Divider")),
            (
                "attachment_hint",
                blocks.StructBlock(
                    [
                        ("note", blocks.TextBlock(required=False)),
                    ],
                    icon="paperclip",
                    label="Attachment Hint (non‑rendered)",
                ),
            ),
        ],
        use_json_field=True,
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('subject'),
        FieldPanel('body'),
        HelpPanel(template="events/admin/emailtemplate_mergevars_help.html", heading="Available merge variables"),
    ]

    def __str__(self):
        return self.title


class EmailCampaign(models.Model):
    event = models.ForeignKey(EventPage, on_delete=models.CASCADE, related_name='email_campaigns')
    template = models.ForeignKey(EmailTemplate, on_delete=models.PROTECT)
    scheduled_for = models.DateTimeField()
    # Audience filters
    include_statuses = models.JSONField(default=list)  # e.g., ["confirmed", "waitlisted"]
    include_type_ids = models.JSONField(default=list)  # list of RegistrationType IDs
    # Optional single attachment via Wagtail Documents
    attachment = models.ForeignKey('wagtaildocs.Document', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    panels = [
        FieldPanel('template'),
        FieldPanel('scheduled_for'),
        FieldPanel('include_statuses'),
        FieldPanel('include_type_ids'),
        FieldPanel('attachment'),
    ]


@register_snippet
class RegistrationFormTemplate(ClusterableModel):
    title = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        MultiFieldPanel(
            [
                InlinePanel("fields", label="Fields"),
            ],
            heading="Form Fields",
            classname="js-registration-fields-inline"
        ),
    ]

    def __str__(self):
        return self.title
