import logging

logger = logging.getLogger('cigionline')


def verify_turnstile_token(token: str, remote_ip: str | None = None) -> bool:
    """Verify a Cloudflare Turnstile token server-side.

    Returns True if the token is valid or if Turnstile is not configured.
    Returns False if verification fails or the network call errors out.
    """
    import requests as http_requests
    from django.conf import settings

    secret = getattr(settings, 'CLOUDFLARE_TURNSTILE_SECRET_KEY', None)
    if not secret:
        return True  # Not configured — skip verification (e.g. local dev)
    if not token:
        return False  # No token submitted

    payload = {'secret': secret, 'response': token}
    if remote_ip:
        payload['remoteip'] = remote_ip

    try:
        resp = http_requests.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data=payload,
            timeout=5,
        )
        result = resp.json()
        return bool(result.get('success', False))
    except Exception:
        logger.exception('Turnstile verification request failed')
        return False
