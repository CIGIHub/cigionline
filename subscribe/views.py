import json
import requests
import hashlib
import mailchimp_marketing as MailchimpMarketing
import logging
from django import forms
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
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


def subscribe_dph(request):
    status = None
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

            member_id = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
            response = client.lists.get_list_member(list_id, member_id)

            if response['status'] == 'unsubscribed':
                status = 'unsubscribed'
            elif response['status'] == 'subscribed':
                status = 'subscribed'
            elif response['status'] == 'pending':
                status = 'pending'
    except Exception as error:
        error_text = (error.text)
        logger.error('An error occurred with Mailchimp: {}'.format(error_text))
        
        if '404' in error_text:
            try:
                response = client.lists.add_list_member(list_id, member_info)
            except Exception as error:
                logger.error('An error occurred with Mailchimp: {}'.format(error.text))
                status = 'error'
            status = 'subscribed_success'
    
    return render(request, 'subscribe/subscribe_page_landing.html', {'status': status, 'subscription_type': 'dph'})
