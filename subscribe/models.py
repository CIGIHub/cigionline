from django import forms
from django.conf import settings
from django.shortcuts import render
from core.models import BasicPageAbstract, SearchablePageAbstract
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from streams.blocks import ParagraphBlock
from newsletters.models import NewsletterPage

import hashlib
from mailchimp_marketing.api_client import ApiClientError
import mailchimp_marketing as MailchimpMarketing
import logging

from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


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

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
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

    mailchimp_tags = []

    def get_mailchimp_tags(self):
        return self.mailchimp_tags

    def get_subscribe_form_class(self):
        return SubscribeForm

    def subscribe_member(self, client, list_id, email, member_info):
        subscriber_hash = hashlib.md5(email.encode("utf-8")).hexdigest()

        response = client.lists.set_list_member(
            list_id,
            subscriber_hash,
            member_info,
        )

        return subscriber_hash, response

    def apply_tags(self, client, list_id, subscriber_hash):
        tags = self.get_mailchimp_tags()
        if not tags:
            return

        client.lists.update_list_member_tags(
            list_id,
            subscriber_hash,
            {
                "tags": [
                    {"name": tag, "status": "active"}
                    for tag in tags
                ]
            },
        )

    def subscribe_to_mailchimp(self, form):
        email = form.cleaned_data["email"].strip().lower()

        member_info = {
            "email_address": email,
            "merge_fields": {
                "FNAME": form.cleaned_data["first_name"],
                "LNAME": form.cleaned_data["last_name"],
                "ORG": form.cleaned_data["organization"],
                "COUNTRY": form.cleaned_data["location"],
            },
            "status_if_new": "pending",  # double opt-in safe
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

        self.apply_tags(client, list_id, subscriber_hash)

        logger.info(f'Successful signup: {response["email_address"]}')

    def serve(self, request):
        form_class = self.get_subscribe_form_class()
        form = form_class()

        context = super().get_context(request)
        context["self"] = self

        if request.GET:
            form = form_class(initial={"email": request.GET.get("email")})

        if request.method == "POST":
            form = form_class(request.POST)

            if form.is_valid():
                try:
                    self.subscribe_to_mailchimp(form)
                except ApiClientError as error:
                    logger.error(f"An error occurred with Mailchimp: {error.text}")

                return render(request, self.landing_page_template, context)

        context["form"] = form
        return render(request, self.template, context)

    class Meta:
        verbose_name = 'Subscribe Page'


class SubscribeForm(forms.Form):
    first_name = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    organization = forms.CharField(required=False, max_length=128, widget=forms.TextInput(attrs={'placeholder': 'Organization*'}))
    location = CountryField(blank=True).formfield(
        required=False,
        widget=CountrySelectWidget(attrs={'placeholder': 'Country*'})
    )
    consent = forms.BooleanField(
        required=True,
        label='',
        widget=forms.CheckboxInput(),
        help_text='I consent to receiving electronic communications from The Center for International Governance Innovation (CIGI), including updates, newsletters and event invitations. I understand that I may withdraw my consent at any time by clicking the unsubscribe link in any email.',
    )


class TFGBVSubscribePage(SubscribePage):
    def get_subscribe_form_class(self):
        return TFGBVSubscribeForm

    mailchimp_tags = ['TFGBV Updates']

    template = '/themes/ogbv/subscribe_page.html'
    landing_page_template = '/themes/ogbv/subscribe_page_landing.html'


class TFGBVSubscribeForm(SubscribeForm):
    affiliation = forms.CharField(required=False, max_length=128, widget=forms.TextInput(attrs={'placeholder': 'Affiliation*'}))

    # help_text wording change from base
    consent = forms.BooleanField(
        required=True,
        label='',
        widget=forms.CheckboxInput(),
        help_text='I consent to receiving electronic communications from The Center for International Governance Innovation (CIGI). I understand that I may withdraw my consent at any time by clicking the unsubscribe link in any email.',
    )

    class Meta(SubscribeForm.Meta):
        # remove unnecessary fields from base form model
        fields = ['first_name', 'last_name', 'email', 'affiliation', 'consent']
