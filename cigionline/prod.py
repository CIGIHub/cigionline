from os import path, environ

if 'BONSAI_URL' in environ:
    WAGTAILSEARCH_BACKENDS = {
        'default': {
            'BACKEND': 'wagtail.search.backends.elasticsearch7',
            'URLS': [environ['BONSAI_URL']],
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

# if 'CLOUDFLARE_EMAIL' in environ \
#         and 'CLOUDFLARE_API_KEY' in environ \
#         and 'CLOUDFLARE_ZONEID' in environ:
#     INSTALLED_APPS = list(INSTALLED_APPS)
#     INSTALLED_APPS.append('wagtail.contrib.frontend_cache')
#     INSTALLED_APPS = tuple(INSTALLED_APPS)
#     WAGTAILFRONTENDCACHE = {
#         'cloudflare': {
#             'BACKEND': 'wagtail.contrib.frontend_cache.backends.CloudflareBackend',
#             'EMAIL': environ['CLOUDFLARE_EMAIL'],
#             'API_KEY': environ['CLOUDFLARE_API_KEY'],
#             'ZONEID': environ['CLOUDFLARE_ZONEID'],
#         },
#     }

# Use AWS S3 for file storage
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3ManifestStaticStorage'
if 'AWS_ACCESS_KEY_ID' in environ:
    AWS_ACCESS_KEY_ID = environ['AWS_ACCESS_KEY_ID']
if 'AWS_SECRET_ACCESS_KEY' in environ:
    AWS_SECRET_ACCESS_KEY = environ['AWS_SECRET_ACCESS_KEY']
if 'AWS_STORAGE_BUCKET_NAME' in environ:
    AWS_STORAGE_BUCKET_NAME = environ['AWS_STORAGE_BUCKET_NAME']
if 'AWS_S3_CUSTOM_DOMAIN' in environ:
    AWS_S3_CUSTOM_DOMAIN = environ['AWS_S3_CUSTOM_DOMAIN']
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False
AWS_PRELOAD_METADATA = True
AWS_S3_FILE_OVERWRITE = False
AWS_LOCATION = 'static'
if 'STATIC_URL' in environ:
    STATIC_URL = environ['STATIC_URL']

EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
if 'SENDGRID_API_KEY' in environ:
    SENDGRID_API_KEY = environ['SENDGRID_API_KEY']

# Mailchimp
if 'MAILCHIMP_API_KEY' in environ:
    MAILCHIMP_API_KEY = environ['MAILCHIMP_API_KEY']
if 'MAILCHIMP_DATA_CENTER' in environ:
    MAILCHIMP_DATA_CENTER = environ['MAILCHIMP_DATA_CENTER']
if 'MAILCHIMP_NEWSLETTER_LIST_ID' in environ:
    MAILCHIMP_NEWSLETTER_LIST_ID = environ['MAILCHIMP_NEWSLETTER_LIST_ID']


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
        },
    },
    'renditions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
}

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

try:
    from .local_env import *  # NOQA
except ImportError as e:
    if 'local_env' not in str(e):
        raise
