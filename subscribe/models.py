from django.db import models
from django.shortcuts import render
from wagtail.core.models import Page
from core.models import BasicPageAbstract
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core.url_routing import RouteResult
from streams.blocks import ParagraphBlock
from django.http.response import Http404

import logging

from django.conf import settings
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError

api_key = settings.MAILCHIMP_API_KEY
server = settings.MAILCHIMP_DATA_CENTER
list_id = settings.MAILCHIMP_NEWSLETTER_LIST_ID

logger = logging.getLogger('subscribe.models')


class SubscribePage(
    Page,
    BasicPageAbstract,
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

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = []
    template = 'subscribe/subscribe_page.html'
    landing_page_template = 'subscribe/subscribe_page_landing.html'

    def serve(self, request):
        context = {
            'self': self,
        }

        if request.GET:
            context['email'] = request.GET['email']

        if request.method == 'POST':
            member_info = {
                'email_address': request.POST['email'],
                'merge_fields': {
                    'FNAME': request.POST['first_name'],
                    'LNAME': request.POST['last_name'],
                    'ORG': request.POST['organization'],
                    'COUNTRY': request.POST['country'],
                }
            }
            try:
                client = MailchimpMarketing.Client()
                client.set_config({
                    'api_key': api_key,
                    'server': server,
                })

                member_info['status'] = 'pending'

                response = client.lists.add_list_member(list_id, member_info)
                print('response: {}'.format(response))

            except ApiClientError as error:
                logger.error('An error occurred with Mailchimp: {}'.format(error.text))

            return render(request, self.landing_page_template, context)

        return render(request, self.template, context)

    class Meta:
        verbose_name = 'Subscribe Page'
