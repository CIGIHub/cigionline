from django.conf import settings
from django.views.generic.base import RedirectView

favicon_view = RedirectView.as_view(url=f'{settings.STATIC_URL}assets/favicon.ico', permanent=True)
