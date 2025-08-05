from urllib.parse import urlencode
from django.conf import settings


def build_auth0_authorization_url(request):
    params = {
        'response_type': 'code',
        'client_id': settings.AUTH0_CLIENT_ID,
        'redirect_uri': settings.AUTH0_REDIRECT_URI,
        'scope': settings.AUTH0_SCOPE,
        'state': request.build_absolute_uri(),
    }
    return f"https://{settings.AUTH0_DOMAIN}/authorize?{urlencode(params)}"
