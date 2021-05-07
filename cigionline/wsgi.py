"""
WSGI config for cigionline project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

if 'PYTHON_ENV' in os.environ and os.environ.get('PYTHON_ENV') == 'admin':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cigionline.settings.admin')
elif 'PYTHON_ENV' in os.environ and os.environ.get('PYTHON_ENV') == 'staging':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cigionline.settings.staging')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cigionline.settings.production')

application = get_wsgi_application()
