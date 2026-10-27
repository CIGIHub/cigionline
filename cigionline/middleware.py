import base64
import os
from django.http import HttpResponse


class EnsureCsrfCookieMiddleware:
    """CSRF plumbing for DS forms on cached pages — scoped, not site-wide.

    Previously this called get_token() on EVERY request, which stamps
    Set-Cookie + Vary: Cookie onto every response and forfeits CDN full-page
    caching. Now:

    - The csrftoken cookie is minted on demand by /csrf/ (core.views
      .csrf_token) — multistep-form.js fetches it when a cookie-less visitor
      lands on a cached form page, then rewrites the baked-in token
      (forms.md, "Caching interaction").
    - The newsletter hand-off POSTs (footer + Subscribe band → /subscribe/
      with prefill=1) carry subscriber PII in the body instead of GET params.
      They are stateless prefill renders — not submissions — originating in
      cached fragments that can't carry a valid token, so exactly those are
      exempted here.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Trailing slash is load-bearing: the slash-less legacy endpoints
        # (/subscribe_dph, /subscribe_think7, /subscribe_digital_finance) are
        # state-changing Mailchimp calls and must keep full CSRF.
        if (
            request.method == 'POST'
            and request.path.startswith('/subscribe/')
            and request.POST.get('prefill')
        ):
            request._dont_enforce_csrf_checks = True
        return self.get_response(request)


class BasicAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'THINK7_DOMAIN' in os.environ:
            target_domain = os.environ.get('THINK7_DOMAIN')

            if request.get_host() == target_domain:
                auth = request.META.get("HTTP_AUTHORIZATION")

                if (
                    "BASIC_AUTH_USER_THINK7" in os.environ and "BASIC_AUTH_PASSWORD_THINK7" in os.environ
                ):
                    BASIC_AUTH_USER_THINK7 = os.environ.get("BASIC_AUTH_USER_THINK7")
                    BASIC_AUTH_PASSWORD_THINK7 = os.environ.get(
                        "BASIC_AUTH_PASSWORD_THINK7"
                    )

                    if auth:
                        auth_type, encoded_credentials = auth.split(" ", 1)
                        if auth_type.lower() == "basic":
                            credentials = base64.b64decode(encoded_credentials).decode(
                                "utf-8"
                            )
                            username, password = credentials.split(":", 1)

                            if (
                                username == BASIC_AUTH_USER_THINK7 and password == BASIC_AUTH_PASSWORD_THINK7
                            ):
                                return self.get_response(request)

                    response = HttpResponse("Unauthorized", status=401)
                    response["WWW-Authenticate"] = 'Basic realm="Protected"'
                    return response

        return self.get_response(request)
