import base64
import os
from django.http import HttpResponse


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
