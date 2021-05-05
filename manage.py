#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    if 'PYTHON_ENV' in os.environ and os.environ.get('PYTHON_ENV') == 'production':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cigionline.settings.production')
    elif 'PYTHON_ENV' in os.environ and os.environ.get('PYTHON_ENV') == 'admin':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cigionline.settings.admin')
    elif 'PYTHON_ENV' in os.environ and os.environ.get('PYTHON_ENV') == 'staging':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cigionline.settings.staging')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cigionline.settings.dev')

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
