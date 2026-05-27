from django import forms
from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from core.models import BasicPageAbstract, SearchablePageAbstract
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from streams.blocks import ParagraphBlock
from newsletters.models import NewsletterPage
from django.db import models

import hashlib
from mailchimp_marketing.api_client import ApiClientError
import mailchimp_marketing as MailchimpMarketing
import logging

from django_countries.fields import CountryField, Country


api_key = None
server = None
list_id = None
if hasattr(settings, 'MAILCHIMP_API_KEY'):
    api_key = settings.MAILCHIMP_API_KEY
if hasattr(settings, 'MAILCHIMP_DATA_CENTER'):
    server = settings.MAILCHIMP_DATA_CENTER
if hasattr(settings, 'MAILCHIMP_NEWSLETTER_LIST_ID'):
    list_id = settings.MAILCHIMP_NEWSLETTER_LIST_ID

logger = logging.getLogger('cigionline')


class SubscribePage(
    Page,
    BasicPageAbstract,
    SearchablePageAbstract,
):
    privacy_note = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'link'],
    )
    landing_page_body = StreamField(
        [
            ('paragraph', ParagraphBlock()),
        ],
        blank=True,
        help_text='The contents of this stream field will be displayed after sign up.',
        use_json_field=True,
    )
    consent_text = models.CharField(
        max_length=500,
        default="I consent to receiving electronic communications from the Centre for International Governance Innovation (CIGI), including updates, newsletters and event invitations. I understand that I may withdraw my consent at any time by clicking the unsubscribe link in any email.",
        help_text='The text that will appear next to the consent checkbox on the subscribe form.',
    )
    button_text = models.CharField(
        blank=True,
        max_length=50,
        help_text='Subscribe CTA button text (e.g. "Sign Up")',
    )
    button_help_text = models.CharField(
        blank=True,
        max_length=500,
        help_text='The text that will appear next to the subscribe CTA button.',
    )

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        MultiFieldPanel(
            [
                FieldPanel('consent_text'),
                FieldPanel('button_text'),
                FieldPanel('button_help_text'),
            ],
            heading='Messaging',
            classname='collapsible',
        ),
        FieldPanel('privacy_note'),
        MultiFieldPanel(
            [
                FieldPanel('landing_page_body'),
            ],
            heading='Landing Page Body',
            classname='collapsible',
        )
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields

    def latest_newsletter(self):
        return NewsletterPage.objects.live().order_by('-first_published_at').first()

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = []
    template = 'subscribe/subscribe_page.html'
    landing_page_template = 'subscribe/subscribe_page_landing.html'

    mailchimp_tag = 'CIGI Weekly Newsletter'
    mailchimp_merge_field_suffix = 'WEEKLY'

    def get_mailchimp_tag(self):
        return self.mailchimp_tag

    def get_mailchimp_suffix(self):
        return self.mailchimp_merge_field_suffix

    def get_subscribe_form_class(self):
        return SubscribeForm

    def get_organization(self, form):
        return form.cleaned_data.get("organization", "")

    def get_country(self, form):
        country = form.cleaned_data.get("location")
        return Country(country).name if country else ""

    def subscribe_member(self, client, list_id, email, member_info):
        subscriber_hash = hashlib.md5(email.encode("utf-8")).hexdigest()

        response = client.lists.set_list_member(
            list_id,
            subscriber_hash,
            member_info,
        )

        return subscriber_hash, response

    def apply_tag(self, client, list_id, subscriber_hash):
        tag = self.get_mailchimp_tag()
        if not tag:
            return

        client.lists.update_list_member_tags(
            list_id,
            subscriber_hash,
            {
                "tags": [
                    {"name": tag, "status": "active"}
                ]
            },
        )

    def get_mailchimp_merge_fields(self, form):
        fields = {
            "FNAME": form.cleaned_data["first_name"],
            "LNAME": form.cleaned_data["last_name"],
            "ORG": self.get_organization(form),
        }

        consent = form.cleaned_data.get("consent", False)
        consent_timestamp = timezone.now().strftime("%m/%d/%Y")
        suffix = self.get_mailchimp_suffix()
        if suffix:
            fields[f"C_{suffix}"] = "Yes" if consent else "No"
            fields[f"C_T_{suffix}"] = consent_timestamp if consent else ""

        country = self.get_country(form)
        if country:
            fields["COUNTRY"] = country

        return fields

    def subscribe_to_mailchimp(self, form):
        if not form.cleaned_data.get("consent", False):
            return

        email = form.cleaned_data["email"].strip().lower()

        member_info = {
            "email_address": email,
            "merge_fields": self.get_mailchimp_merge_fields(form),
            "status_if_new": "subscribed",
        }

        if not (api_key and server and list_id):
            return

        client = MailchimpMarketing.Client()
        client.set_config({
            "api_key": api_key,
            "server": server,
        })

        subscriber_hash, response = self.subscribe_member(
            client, list_id, email, member_info
        )

        self.apply_tag(client, list_id, subscriber_hash)

        logger.info(f'Successful signup: {response["email_address"]}')

    def serve(self, request):
        from utils.security import verify_turnstile_token

        form_class = self.get_subscribe_form_class()
        form = form_class(
            request.POST or None,
            consent_text=self.consent_text,
        )

        context = super().get_context(request)
        context["self"] = self
        context["turnstile_site_key"] = getattr(settings, "CLOUDFLARE_TURNSTILE_SITE_KEY", "")

        if request.GET:
            form = form_class(
                initial={"email": request.GET.get("email")},
                consent_text=self.consent_text,
            )

        if request.method == "POST":
            turnstile_token = request.POST.get("cf-turnstile-response", "")
            if not verify_turnstile_token(turnstile_token, request.META.get("REMOTE_ADDR")):
                logger.warning("Turnstile verification failed for subscribe form")
                # Silently succeed without subscribing — don't leak bot detection
                context["form"] = form_class(consent_text=self.consent_text)
                return render(request, self.landing_page_template, context)

            form = form_class(
                request.POST,
                consent_text=self.consent_text,
            )

            if form.is_valid():
                consent = form.cleaned_data.get("consent", False)

                if consent:
                    try:
                        self.subscribe_to_mailchimp(form)
                    except ApiClientError as error:
                        logger.error(f"An error occurred with Mailchimp: {error.text}")
                else:
                    logger.info("User did not consent; skipping Mailchimp subscription.")

                context["form"] = form
                return render(request, self.landing_page_template, context)

        context["form"] = form
        return render(request, self.template, context)

    class Meta:
        verbose_name = 'Subscribe Page'


class SubscribeForm(forms.Form):
    first_name = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    organization = forms.CharField(required=True, max_length=128, widget=forms.TextInput(attrs={'placeholder': 'Organization'}))
    location = CountryField(blank=True).formfield(
        required=True,
        empty_label="Country",
        widget=forms.Select()
    )
    consent = forms.BooleanField(
        required=True,
        label='',
        widget=forms.CheckboxInput(),
    )

    def __init__(self, *args, consent_text='', **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['consent'].help_text = consent_text


class TFGBVSubscribePage(SubscribePage):
    def get_subscribe_form_class(self):
        return TFGBVSubscribeForm

    def get_organization(self, form):
        return form.cleaned_data.get("affiliation", "")

    def get_country(self, form):
        return None

    mailchimp_tag = 'TFGBV Updates'
    mailchimp_merge_field_suffix = 'TFGBV'
    parent_page_types = ['research.ProjectPage']
    template = 'themes/ogbv/subscribe_page.html'
    landing_page_template = 'themes/ogbv/subscribe_page_landing.html'


class TFGBVSubscribeForm(SubscribeForm):
    affiliation = forms.CharField(required=False, max_length=128, widget=forms.TextInput(attrs={'placeholder': 'Affiliation*'}))

    # help_text wording change from base
    consent = forms.BooleanField(
        required=True,
        label='',
        widget=forms.CheckboxInput(),
    )

    allowed_fields = [
        'first_name',
        'last_name',
        'email',
        'affiliation',
        'consent',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = {
            name: self.fields[name]
            for name in self.allowed_fields
            if name in self.fields
        }
