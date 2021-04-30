from .base import *

DEBUG = False

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

if 'CLOUDFLARE_EMAIL' in os.environ \
        and 'CLOUDFLARE_API_KEY' in os.environ \
        and 'CLOUDFLARE_ZONEID' in os.environ:
    INSTALLED_APPS = list(INSTALLED_APPS)
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
AWS_LOCATION = 'static'
if 'STATIC_URL' in os.environ:
    STATIC_URL = os.environ['STATIC_URL']

EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
if 'SENDGRID_API_KEY' in os.environ:
    SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']

# Mailchimp
if 'MAILCHIMP_API_KEY' in os.environ:
    MAILCHIMP_API_KEY = os.environ['MAILCHIMP_API_KEY']
if 'MAILCHIMP_DATA_CENTER' in os.environ:
    MAILCHIMP_DATA_CENTER = os.environ['MAILCHIMP_DATA_CENTER']
if 'MAILCHIMP_NEWSLETTER_LIST_ID' in os.environ:
    MAILCHIMP_NEWSLETTER_LIST_ID = os.environ['MAILCHIMP_NEWSLETTER_LIST_ID']




from os import path

__author__ = 'snake'

SECRET_KEY = None  # ./local_env.py
DB_USER = 'cigionline'
DB_NAME = 'cigionline'
DB_PASS = 'fk03989vbtuuik3uy457gf84dijw0pfg0-ekrn4by34foidjb'
ALLOWED_HOSTS = (
    '159.203.12.201',
    'cigionline.webisoft.org',
)
PROJECT_DOMAIN = 'https://cigionline.webisoft.org'


DEBUG = False
PROJECT_NAME = path.basename(path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': DB_USER,
        'NAME': DB_NAME,
        'PASSWORD': DB_PASS,
        'HOST': 'localhost',
        'CONN_MAX_AGE': 30,
        'OPTIONS': {
            'sslmode': 'disable',
        },
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'ssl_cert_reqs': False,
            },
        },
    },
    'renditions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'ssl_cert_reqs': False,
            },
        },
    },
}


SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'redis'

STATICFILES_STORAGE = 'libs.storage.CacheBustingStaticFilesStorage'

try:
    from .local_env import *
except ImportError as e:
    if 'local_env' not in str(e):
        raise
