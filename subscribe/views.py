import json
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

api_key = None
server = None
list_id = None
if hasattr(settings, 'MAILCHIMP_API_KEY_DPH'):
    api_key = settings.MAILCHIMP_API_KEY
if hasattr(settings, 'MAILCHIMP_DATA_CENTER_DPH'):
    server = settings.MAILCHIMP_DATA_CENTER
if hasattr(settings, 'MAILCHIMP_NEWSLETTER_LIST_ID_DPH'):
    list_id = settings.MAILCHIMP_NEWSLETTER_LIST_ID


@csrf_exempt
@require_POST
def subscribe_dph(request):
    email = request.POST.get('email')
    if not email:
        return JsonResponse({'error': 'Email is required'}, status=400)

    url = f'https://{server}.api.mailchimp.com/3.0/lists/{list_id}/members/'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'email_address': email,
        'status': 'subscribed'
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return JsonResponse({'message': 'Subscription successful'})
    else:
        return JsonResponse({'error': 'Subscription failed', 'details': response.json()}, status=response.status_code)
