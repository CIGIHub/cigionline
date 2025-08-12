import jwt
import requests
import time
from jwt.algorithms import RSAAlgorithm
from urllib.parse import urlencode
from django.conf import settings


def build_auth0_authorization_url(request):
    params = {
        'response_type': 'code',
        'client_id': settings.AUTH0_CLIENT_ID,
        'redirect_uri': settings.AUTH0_REDIRECT_URI,
        'scope': settings.AUTH0_SCOPE,
        'audience': settings.AUTH0_AUDIENCE,
        'state': request.build_absolute_uri(),
    }
    return f'https://{settings.AUTH0_DOMAIN}/authorize?{urlencode(params)}'


_JWKS, _JWKS_TS = None, 0


def _get_jwks():
    global _JWKS, _JWKS_TS
    if not _JWKS or time.time() - _JWKS_TS > 3600:
        url = f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json'
        _JWKS = requests.get(url, timeout=5).json()
        _JWKS_TS = time.time()
    return _JWKS


def decode_and_verify(token: str) -> dict:
    jwks = _get_jwks()
    header = jwt.get_unverified_header(token)
    key = next((k for k in jwks['keys'] if k['kid'] == header['kid']), None)
    if not key:
        raise jwt.InvalidTokenError('Unknown kid')
    public_key = RSAAlgorithm.from_jwk(key)
    return jwt.decode(
        token,
        public_key,
        algorithms=['RS256'],
        audience=settings.AUTH0_AUDIENCE,
        issuer=f'https://{settings.AUTH0_DOMAIN}/'
    )
