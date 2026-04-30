import hashlib
import json
import mailchimp_marketing as MailchimpMarketing
import logging
from fnmatch import fnmatch
from django import forms
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from mailchimp_marketing.api_client import ApiClientError

logger = logging.getLogger('cigionline')
api_key = None
server = None
list_id = None
SECOND_CENTURY_COMMISSION_TAG = 'Second Century Commission'
SECOND_CENTURY_COMMISSION_FIELD_ALIASES = {
    'EMAIL': ('EMAIL', 'email'),
    'FNAME': ('FNAME', 'first_name', 'fname'),
    'LNAME': ('LNAME', 'last_name', 'lname'),
    'CONSENT': ('CONSENT', 'consent'),
}

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


class SecondCenturyCommissionSubscribeForm(forms.Form):
    EMAIL = forms.EmailField(max_length=254, required=True)
    FNAME = forms.CharField(max_length=128, required=True)
    LNAME = forms.CharField(max_length=128, required=True)
    CONSENT = forms.CharField(max_length=3, required=True)


def _add_second_century_commission_cors_headers(request, response):
    allowed_origins = getattr(settings, 'SECOND_CENTURY_COMMISSION_ALLOWED_ORIGINS', None)
    origin = request.headers.get('Origin')
    requested_headers = request.headers.get('Access-Control-Request-Headers')

    if isinstance(allowed_origins, str):
        allowed_origins = [item.strip() for item in allowed_origins.split(',') if item.strip()]

    if allowed_origins:
        if '*' in allowed_origins:
            response['Access-Control-Allow-Origin'] = '*'
        elif origin and any(fnmatch(origin, allowed_origin) for allowed_origin in allowed_origins):
            response['Access-Control-Allow-Origin'] = origin
            response['Vary'] = 'Origin'
    else:
        response['Access-Control-Allow-Origin'] = '*'

    response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response['Access-Control-Allow-Headers'] = requested_headers or 'Content-Type, X-Requested-With'
    response['Access-Control-Max-Age'] = '86400'
    return response


def _second_century_commission_json_response(request, data, status=200):
    response = JsonResponse(data, status=status)
    return _add_second_century_commission_cors_headers(request, response)


def _get_second_century_commission_request_data(request):
    content_type = request.META.get('CONTENT_TYPE', '').split(';')[0].strip().lower()
    if content_type == 'application/json':
        try:
            return json.loads(request.body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    return request.POST


def _normalize_second_century_commission_data(data):
    normalized = {}
    for field_name, aliases in SECOND_CENTURY_COMMISSION_FIELD_ALIASES.items():
        for alias in aliases:
            value = data.get(alias)
            if value not in (None, ''):
                normalized[field_name] = value
                break
    return normalized


@csrf_exempt
@require_http_methods(['POST', 'OPTIONS'])
def subscribe_second_century_commission(request):
    if request.method == 'OPTIONS':
        response = HttpResponse(status=204)
        return _add_second_century_commission_cors_headers(request, response)

    data = _get_second_century_commission_request_data(request)
    if data is None or not hasattr(data, 'get'):
        return _second_century_commission_json_response(
            request,
            {'success': False, 'error': 'Invalid request data'},
            status=400,
        )

    form = SecondCenturyCommissionSubscribeForm(_normalize_second_century_commission_data(data))
    if not form.is_valid():
        return _second_century_commission_json_response(
            request,
            {'success': False, 'errors': form.errors.get_json_data()},
            status=400,
        )

    mailchimp_api_key = getattr(settings, 'MAILCHIMP_API_KEY', None)
    mailchimp_server = getattr(settings, 'MAILCHIMP_DATA_CENTER', None)
    mailchimp_list_id = getattr(settings, 'MAILCHIMP_NEWSLETTER_LIST_ID', None)
    if not mailchimp_api_key or not mailchimp_server or not mailchimp_list_id:
        logger.error('Second Century Commission Mailchimp configuration is missing')
        return _second_century_commission_json_response(
            request,
            {'success': False, 'error': 'Mailchimp configuration is missing'},
            status=503,
        )

    email = form.cleaned_data['EMAIL']
    member_id = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    member_info = {
        'email_address': email,
        'status_if_new': 'pending',
        'merge_fields': {
            'FNAME': form.cleaned_data['FNAME'],
            'LNAME': form.cleaned_data['LNAME'],
            'CONSENT': form.cleaned_data['CONSENT'],
        },
    }
    tag_info = {
        'tags': [
            {
                'name': SECOND_CENTURY_COMMISSION_TAG,
                'status': 'active',
            },
        ],
    }

    try:
        client = MailchimpMarketing.Client()
        client.set_config({
            'api_key': mailchimp_api_key,
            'server': mailchimp_server,
        })

        response = client.lists.set_list_member(mailchimp_list_id, member_id, member_info)
        status = response.get('status')

        if status in ['cleaned', 'unsubscribed']:
            return _second_century_commission_json_response(
                request,
                {
                    'success': False,
                    'status': status,
                    'error': 'This email address cannot be subscribed through this form',
                },
                status=409,
            )

        client.lists.update_list_member_tags(mailchimp_list_id, member_id, tag_info)
        logger.info(f'Successful Second Century Commission sign up: {email}')
    except ApiClientError as error:
        logger.error('An error occurred with Mailchimp: {}'.format(error.text))
        return _second_century_commission_json_response(
            request,
            {'success': False, 'error': 'Mailchimp subscription failed'},
            status=502,
        )

    return _second_century_commission_json_response(
        request,
        {
            'success': True,
            'status': status,
            'email': email,
        },
    )


def subscribe_dph(request):
    status = None
    email = None
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
    except ApiClientError as error:
        error_text = (error.text)
        logger.error('An error occurred with Mailchimp: {}'.format(error_text))

        if '404' in error_text:
            try:
                response = client.lists.add_list_member(list_id, member_info)
            except ApiClientError as error:
                logger.error('An error occurred with Mailchimp: {}'.format(error.text))
                status = 'error'
            status = 'subscribed_success'

    return render(request, 'subscribe/subscribe_page_landing.html', {'status': status, 'subscription_type': 'dph'})


def subscribe_think7(request):
    api_key = None
    server = None
    list_id = None

    if hasattr(settings, 'MAILCHIMP_API_KEY_THINK7'):
        api_key = settings.MAILCHIMP_API_KEY_THINK7
    if hasattr(settings, 'MAILCHIMP_DATA_CENTER_THINK7'):
        server = settings.MAILCHIMP_DATA_CENTER_THINK7
    if hasattr(settings, 'MAILCHIMP_NEWSLETTER_LIST_ID_THINK7'):
        list_id = settings.MAILCHIMP_NEWSLETTER_LIST_ID_THINK7

    status = None
    email = None
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
    except ApiClientError as error:
        error_text = (error.text)
        logger.error('An error occurred with Mailchimp: {}'.format(error_text))

        if '404' in error_text:
            try:
                response = client.lists.add_list_member(list_id, member_info)
            except ApiClientError as error:
                logger.error('An error occurred with Mailchimp: {}'.format(error.text))
                status = 'error'
            status = 'subscribed_success'

    return render(request, 'think7/subscribe_page_landing.html', {'status': status, 'subscription_type': 'think7'})


def subscribe_digital_finance(request):
    api_key = None
    server = None
    list_id = None

    if hasattr(settings, 'MAILCHIMP_API_KEY_DIGITAL_FINANCE'):
        api_key = settings.MAILCHIMP_API_KEY_DIGITAL_FINANCE
    if hasattr(settings, 'MAILCHIMP_DATA_CENTER_DIGITAL_FINANCE'):
        server = settings.MAILCHIMP_DATA_CENTER_DIGITAL_FINANCE
    if hasattr(settings, 'MAILCHIMP_NEWSLETTER_LIST_ID_DIGITAL_FINANCE'):
        list_id = settings.MAILCHIMP_NEWSLETTER_LIST_ID_DIGITAL_FINANCE
    print(api_key, server, list_id)
    status = None
    email = None
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
            print(response)

            if response['status'] == 'unsubscribed':
                status = 'unsubscribed'
            elif response['status'] == 'subscribed':
                status = 'subscribed'
            elif response['status'] == 'pending':
                status = 'pending'
    except ApiClientError as error:
        error_text = (error.text)
        logger.error('An error occurred with Mailchimp: {}'.format(error_text))

        if '404' in error_text:
            try:
                response = client.lists.add_list_member(list_id, member_info)
                print(response)
            except ApiClientError as error:
                logger.error('An error occurred with Mailchimp: {}'.format(error.text))
                status = 'error'
            status = 'subscribed_success'

    return render(request, 'subscribe/subscribe_page_landing.html', {'status': status, 'subscription_type': 'digital_finance'})
