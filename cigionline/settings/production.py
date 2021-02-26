import dj_database_url
import os
from .base import *

DEBUG = False

try:
    from .local import *
except ImportError:
    pass

if 'SECRET_KEY' in os.environ:
    SECRET_KEY = os.environ['SECRET_KEY']

if 'ALLOWED_HOSTS' in os.environ:
    ALLOWED_HOSTS = [os.environ['ALLOWED_HOSTS']]

if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }

if 'BONSAI_URL' in os.environ:
    WAGTAILSEARCH_BACKENDS = {
        'default': {
            'BACKEND': 'wagtail.search.backends.elasticsearch7',
            'URLS': [os.environ['BONSAI_URL']],
            'INDEX': 'wagtail',
            'TIMEOUT': 30,
            'OPTIONS': {},
            'INDEX_SETTINGS': {},
        },
    }

# Cache everything for 10 minutes
# This only applies to pages that do not have a more specific cache-control
# setting. See urls.py
CACHE_CONTROL_MAX_AGE = 600

if 'REDIS_URL' in os.environ:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ['REDIS_URL'],
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'ssl_cert_reqs': False,
                },
            },
        },
        'renditions': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ['REDIS_URL'],
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'ssl_cert_reqs': False,
                },
            },
        },
    }

if 'CLOUDFLARE_EMAIL' in os.environ \
        and 'CLOUDFLARE_API_KEY' in os.environ \
        and 'CLOUDFLARE_ZONEID' in os.environ:
    WAGTAILFRONTENDCACHE = {
        'cloudflare': {
            'BACKEND': 'wagtail.contrib.frontend_cache.backends.CloudflareBackend',
            'EMAIL': os.environ['CLOUDFLARE_EMAIL'],
            'API_KEY': os.environ['CLOUDFLARE_API_KEY'],
            'ZONEID': os.environ['CLOUDFLARE_ZONEID'],
        },
    }

# Use AWS S3 for file storage
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
if 'AWS_ACCESS_KEY_ID' in os.environ:
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
if 'AWS_SECRET_ACCESS_KEY' in os.environ:
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
if 'AWS_STORAGE_BUCKET_NAME' in os.environ:
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
if 'AWS_S3_CUSTOM_DOMAIN' in os.environ:
    AWS_S3_CUSTOM_DOMAIN = os.environ['AWS_S3_CUSTOM_DOMAIN']
AWS_DEFAULT_ACL = None
AWS_LOCATION = 'static'
if 'STATIC_URL' in os.environ:
    STATIC_URL = os.environ['STATIC_URL']

EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
if 'SENDGRID_API_KEY' in os.environ:
    SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']
