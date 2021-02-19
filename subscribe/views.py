from django.shortcuts import render, redirect
from django.contrib import messages
import logging

from django.conf import settings
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError

api_key = settings.MAILCHIMP_API_KEY
server = settings.MAILCHIMP_DATA_CENTER
list_id = settings.MAILCHIMP_NEWSLETTER_LIST_ID

logger = logging.getLogger('subscribe.views')


def redirect_subscribe(request):
    return render(request, 'subscribe/subscribe_page.html', {'email': request.GET['email']})


def subscribe(member_info):
    try:
        client = MailchimpMarketing.Client()
        client.set_config({
            'api_key': api_key,
            'server': server,
        })

        member_info['status'] = 'pending'

        response = client.lists.add_list_member(list_id, member_info)
        print('response: {}'.format(response))

        return True

    except ApiClientError as error:
        logger.error('An error occurred with Mailchimp: {}'.format(error.text))

        return False


def subscription(request):
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

        if subscribe(member_info):
            return render(request, 'subscribe/subscribe_page_landing.html', {'success': True})
        else:
            return render(request, 'subscribe/subscribe_page_landing.html', {'success': False})
