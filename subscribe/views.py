import json
import requests
import mailchimp_marketing as MailchimpMarketing
import logging
from django import forms
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from mailchimp_marketing.api_client import ApiClientError

logger = logging.getLogger('cigionline')
api_key = None
server = None
list_id = None

if hasattr(settings, 'MAILCHIMP_API_KEY_DPH'):
    api_key = settings.MAILCHIMP_API_KEY_DPH
if hasattr(settings, 'MAILCHIMP_DATA_CENTER_DPH'):
    server = settings.MAILCHIMP_DATA_CENTER_DPH
if hasattr(settings, 'MAILCHIMP_NEWSLETTER_LIST_ID_DPH'):
    list_id = settings.MAILCHIMP_NEWSLETTER_LIST_ID_DPH


class EmailOnlySubscribeForm(forms.Form):
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email'
    }))


@csrf_protect
@require_POST
def subscribe_dph(request):
    form = EmailOnlySubscribeForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        member_info = {
            'email_address': email,
            'status': 'pending'
        }

    if not email:
        return JsonResponse({'error': 'Email is required'}, status=400)

    try:
        if api_key and server and list_id:
            client = MailchimpMarketing.Client()
            client.set_config({
                'api_key': api_key,
                'server': server,
            })

            response = client.lists.add_list_member(list_id, member_info)
            if response['status'] == 'pending':
                logger.info(f'Successful newsletter sign up: {response["email_address"]}')
                return JsonResponse({'message': 'Subscription successful'}, status=200)

    except ApiClientError as error:
        logger.error('An error occurred with Mailchimp: {}'.format(error.text))
        response_text = json.loads(error.text)

        if response_text['title'] == 'Member Exists':
            return JsonResponse({'error': 'Subscription failed', 'details': 'Email already exists'}, status=400)
        return JsonResponse({'error': 'Subscription failed', 'details': 'failed'}, status=500)
