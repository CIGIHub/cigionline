import hashlib
import mailchimp_marketing as MailchimpMarketing
import logging
from django import forms
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from mailchimp_marketing.api_client import ApiClientError

logger = logging.getLogger('cigionline')


class EmailOnlySubscribeForm(forms.Form):
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email'
    }))


def _get_mailchimp_config(list_key):
    mapping = {
        'dph': {
            'api_key': 'MAILCHIMP_API_KEY_DPH',
            'server': 'MAILCHIMP_DATA_CENTER_DPH',
            'list_id': 'MAILCHIMP_NEWSLETTER_LIST_ID_DPH',
            'template': 'subscribe/subscribe_page_landing.html',
            'subscription_type': 'dph',
        },
        'think7': {
            'api_key': 'MAILCHIMP_API_KEY_THINK7',
            'server': 'MAILCHIMP_DATA_CENTER_THINK7',
            'list_id': 'MAILCHIMP_NEWSLETTER_LIST_ID_THINK7',
            'template': 'think7/subscribe_page_landing.html',
            'subscription_type': 'think7',
        },
        'digital_finance': {
            'api_key': 'MAILCHIMP_API_KEY_DIGITAL_FINANCE',
            'server': 'MAILCHIMP_DATA_CENTER_DIGITAL_FINANCE',
            'list_id': 'MAILCHIMP_NEWSLETTER_LIST_ID_DIGITAL_FINANCE',
            'template': 'subscribe/subscribe_page_landing.html',
            'subscription_type': 'digital_finance',
        },
        'safer_digital_spaces': {
            'api_key': 'MAILCHIMP_API_KEY_SAFER_DIGITAL_SPACES',
            'server': 'MAILCHIMP_DATA_CENTER_SAFER_DIGITAL_SPACES',
            'list_id': 'MAILCHIMP_NEWSLETTER_LIST_ID_SAFER_DIGITAL_SPACES',
            'template': 'subscribe/subscribe_page_landing.html',
            'subscription_type': 'safer_digital_spaces',
        }
    }

    cfg = mapping.get(list_key)
    if not cfg:
        return None

    return {
        'api_key': getattr(settings, cfg['api_key'], None),
        'server': getattr(settings, cfg['server'], None),
        'list_id': getattr(settings, cfg['list_id'], None),
        'template': cfg['template'],
        'subscription_type': cfg['subscription_type'],
    }


def _handle_mailchimp_subscription(api_key, server, list_id, email):
    client = MailchimpMarketing.Client()
    client.set_config({'api_key': api_key, 'server': server})

    member_id = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    member_info = {'email_address': email, 'status': 'pending'}

    try:
        response = client.lists.get_list_member(list_id, member_id)
        status = None
        if response.get('status') == 'unsubscribed':
            status = 'unsubscribed'
        elif response.get('status') == 'subscribed':
            status = 'subscribed'
        elif response.get('status') == 'pending':
            status = 'pending'
        return status
    except ApiClientError as error:
        error_text = getattr(error, 'text', str(error))
        logger.error('An error occurred with Mailchimp: %s', error_text)
        # If member not found, add them
        if '404' in error_text:
            try:
                client.lists.add_list_member(list_id, member_info)
                return 'subscribed_success'
            except ApiClientError as error:
                logger.error('An error occurred adding member to Mailchimp: %s', getattr(error, 'text', str(error)))
                return 'error'
        return 'error'


def subscribe_to_list(request, list_key):
    cfg = _get_mailchimp_config(list_key)
    if not cfg:
        return JsonResponse({'error': 'Unknown list'}, status=400)

    form = EmailOnlySubscribeForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'Email is required'}, status=400)

    email = form.cleaned_data['email']
    api_key = cfg['api_key']
    server = cfg['server']
    list_id = cfg['list_id']

    if not (api_key and server and list_id):
        logger.error('Missing Mailchimp configuration for list: %s', list_key)
        return JsonResponse({'error': 'Mailchimp configuration missing for this list'}, status=500)

    status = _handle_mailchimp_subscription(api_key, server, list_id, email)
    print(status)
    print(cfg['subscription_type'])

    return render(request, cfg['template'], {'status': status, 'subscription_type': cfg['subscription_type']})
