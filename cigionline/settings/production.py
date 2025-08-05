import dj_database_url
import os
import json
import base64
from .base import *  # noqa: F403

DEBUG = False

ADMIN_ENABLED = True

try:
    from .local import *  # noqa: F403
except ImportError:
    pass

if 'SECRET_KEY' in os.environ:
    SECRET_KEY = os.environ['SECRET_KEY']

if 'ALLOWED_HOSTS' in os.environ:
    ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')

if 'WAGTAILADMIN_BASE_URL' in os.environ:
    WAGTAILADMIN_BASE_URL = os.environ['WAGTAILADMIN_BASE_URL']

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
            'TIMEOUT': 300,
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
            'TIMEOUT': 31536000,
            'OPTIONS': {
                'MAX_RETRIES': 200,
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
    INSTALLED_APPS = list(INSTALLED_APPS)  # noqa: F405
    INSTALLED_APPS.append('wagtail.contrib.frontend_cache')
    INSTALLED_APPS = tuple(INSTALLED_APPS)
    WAGTAILFRONTENDCACHE = {
        'cloudflare': {
            'BACKEND': 'wagtail.contrib.frontend_cache.backends.CloudflareBackend',
            'EMAIL': os.environ['CLOUDFLARE_EMAIL'],
            'API_KEY': os.environ['CLOUDFLARE_API_KEY'],
            'ZONEID': os.environ['CLOUDFLARE_ZONEID'],
        },
    }

PLATFORMSH_DB_RELATIONSHIP = "postgresql"

if (os.getenv('PLATFORM_PROJECT_ENTROPY') is not None):
    SECRET_KEY = os.getenv('PLATFORM_PROJECT_ENTROPY')

if 'PLATFORM_RELATIONSHIPS' in os.environ:
    PLATFORM_RELATIONSHIPS = json.loads(base64.b64decode(os.environ['PLATFORM_RELATIONSHIPS']))

    if 'postgresql' in PLATFORM_RELATIONSHIPS:
        db_settings = PLATFORM_RELATIONSHIPS[PLATFORMSH_DB_RELATIONSHIP][0]
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': db_settings['path'],
                'USER': db_settings['username'],
                'PASSWORD': db_settings['password'],
                'HOST': db_settings['host'],
                'PORT': db_settings['port'],
            }
        }

    if 'redis' in PLATFORM_RELATIONSHIPS:
        redis_info = PLATFORM_RELATIONSHIPS['redis'][0]
        redis_url = f"redis://{redis_info['host']}:{redis_info['port']}"
        CACHES = {
            'default': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': redis_url,
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                },
            },
            'renditions': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': redis_url,
                'TIMEOUT': 31536000,
                'OPTIONS': {
                    'MAX_RETRIES': 200,
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                },
            },
        }

    if 'elasticsearch' in PLATFORM_RELATIONSHIPS:
        es_info = PLATFORM_RELATIONSHIPS['elasticsearch'][0]
        es_host = es_info['host']
        es_port = es_info['port']

        WAGTAILSEARCH_BACKENDS = {
            'default': {
                'BACKEND': 'wagtail.search.backends.elasticsearch7',
                'URLS': [f'http://{es_host}:{es_port}'],
                'INDEX': 'wagtail',
                'TIMEOUT': 30,
                'OPTIONS': {},
                'INDEX_SETTINGS': {},
            },
        }

# Use AWS S3 for file storage
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3ManifestStaticStorage'
if 'AWS_ACCESS_KEY_ID' in os.environ:
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
if 'AWS_SECRET_ACCESS_KEY' in os.environ:
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
if 'AWS_STORAGE_BUCKET_NAME' in os.environ:
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
if 'AWS_S3_CUSTOM_DOMAIN' in os.environ:
    AWS_S3_CUSTOM_DOMAIN = os.environ['AWS_S3_CUSTOM_DOMAIN']
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False
AWS_PRELOAD_METADATA = True
AWS_S3_FILE_OVERWRITE = False
AWS_S3_OBJECT_PARAMETERS = {
    "ACL": "public-read"
}
AWS_LOCATION = 'static'
if 'STATIC_URL' in os.environ:
    STATIC_URL = os.environ['STATIC_URL']

if 'WAGTAILADMIN_NOTIFICATION_FROM_EMAIL' in os.environ:
    WAGTAILADMIN_NOTIFICATION_FROM_EMAIL = os.environ['WAGTAILADMIN_NOTIFICATION_FROM_EMAIL']

# Mailchimp
if 'MAILCHIMP_API_KEY' in os.environ:
    MAILCHIMP_API_KEY = os.environ['MAILCHIMP_API_KEY']
if 'MAILCHIMP_DATA_CENTER' in os.environ:
    MAILCHIMP_DATA_CENTER = os.environ['MAILCHIMP_DATA_CENTER']
if 'MAILCHIMP_NEWSLETTER_LIST_ID' in os.environ:
    MAILCHIMP_NEWSLETTER_LIST_ID = os.environ['MAILCHIMP_NEWSLETTER_LIST_ID']

if 'MAILCHIMP_API_KEY_DPH' in os.environ:
    MAILCHIMP_API_KEY_DPH = os.environ['MAILCHIMP_API_KEY_DPH']
if 'MAILCHIMP_DATA_CENTER_DPH' in os.environ:
    MAILCHIMP_DATA_CENTER_DPH = os.environ['MAILCHIMP_DATA_CENTER_DPH']
if 'MAILCHIMP_NEWSLETTER_LIST_ID_DPH' in os.environ:
    MAILCHIMP_NEWSLETTER_LIST_ID_DPH = os.environ['MAILCHIMP_NEWSLETTER_LIST_ID_DPH']

if 'MAILCHIMP_API_KEY_THINK7' in os.environ:
    MAILCHIMP_API_KEY_THINK7 = os.environ['MAILCHIMP_API_KEY_THINK7']
if 'MAILCHIMP_DATA_CENTER_THINK7' in os.environ:
    MAILCHIMP_DATA_CENTER_THINK7 = os.environ['MAILCHIMP_DATA_CENTER_THINK7']
if 'MAILCHIMP_NEWSLETTER_LIST_ID_THINK7' in os.environ:
    MAILCHIMP_NEWSLETTER_LIST_ID_THINK7 = os.environ['MAILCHIMP_NEWSLETTER_LIST_ID_THINK7']

if 'THINK7_SENDGRID_API_KEY' in os.environ:
    THINK7_SENDGRID_API_KEY = os.environ['THINK7_SENDGRID_API_KEY']

if 'THINK7_SENDGRID_EMAIL_RECIPIENT' in os.environ:
    THINK7_SENDGRID_EMAIL_RECIPIENT = os.environ['THINK7_SENDGRID_EMAIL_RECIPIENT']

if 'DIGITAL_FINANCE_SENDGRID_API' in os.environ:
    DIGITAL_FINANCE_SENDGRID_API = os.environ['DIGITAL_FINANCE_SENDGRID_API']
if 'DIGITAL_FINANCE_EMAIL_RECIPIENT' in os.environ:
    DIGITAL_FINANCE_EMAIL_RECIPIENT = os.environ['DIGITAL_FINANCE_EMAIL_RECIPIENT']

if 'DOCUMENT_UPLOAD_PASSWORD' in os.environ:
    DOCUMENT_UPLOAD_PASSWORD = os.environ['DOCUMENT_UPLOAD_PASSWORD']

WAGTAIL_2FA_REQUIRED = True
