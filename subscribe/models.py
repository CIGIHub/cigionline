from django import forms
from django.conf import settings
from django.shortcuts import render
from core.models import BasicPageAbstract, SearchablePageAbstract
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from streams.blocks import ParagraphBlock

from mailchimp_marketing.api_client import ApiClientError
import mailchimp_marketing as MailchimpMarketing
import logging

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
    )

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        FieldPanel('privacy_note'),
        MultiFieldPanel(
            [
                StreamFieldPanel('landing_page_body'),
            ],
            heading='Landing Page Body',
            classname='collapsible',
        )
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = []
    template = 'subscribe/subscribe_page.html'
    landing_page_template = 'subscribe/subscribe_page_landing.html'

    def serve(self, request):
        form = SubscribeForm()
        context = {
            'self': self,
        }
        member_info = {}

        if request.GET:
            form = SubscribeForm(initial={'email': request.GET.get('email', None)})

        if request.method == 'POST':
            form = SubscribeForm(request.POST)
            if form.is_valid():
                member_info['email_address'] = form.cleaned_data['email']
                member_info['merge_fields'] = {
                    'FNAME': form.cleaned_data['first_name'],
                    'LNAME': form.cleaned_data['last_name'],
                    'ORG': form.cleaned_data['organization'],
                    'COUNTRY': form.cleaned_data['country'],
                }

            try:
                if api_key and server and list_id:
                    client = MailchimpMarketing.Client()
                    client.set_config({
                        'api_key': api_key,
                        'server': server,
                    })

                    member_info['status'] = 'pending'

                    response = client.lists.add_list_member(list_id, member_info)
                    logger.info(f'Successful newsletter sign up: {response["email_address"]}')

            except ApiClientError as error:
                logger.error('An error occurred with Mailchimp: {}'.format(error.text))

            return render(request, self.landing_page_template, context)

        context['form'] = form
        return render(request, self.template, context)

    class Meta:
        verbose_name = 'Subscribe Page'


class SubscribeForm(forms.Form):
    confirmation = forms.BooleanField(label='CIGI Newsletter - A weekly newsletter featuring highlights of major CIGI announcements, publications, events, videos and other news.', initial=True)
    first_name = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'placeholder': 'First Name*'}))
    last_name = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'placeholder': 'Last Name*'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address*'}))
    organization = forms.CharField(required=False, max_length=128, widget=forms.TextInput(attrs={'placeholder': 'Organization'}))
    country = forms.CharField(required=False, max_length=128, widget=forms.TextInput(attrs={'placeholder': 'Country'}))
