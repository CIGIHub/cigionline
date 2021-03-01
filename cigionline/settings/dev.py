from .base import *
from dotenv import load_dotenv

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'a%86$z=ubc$(fh7@eqli92u!0t03#q-bq3=_trv1nn2+a=_5$n'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Uncomment this to enable Django debug toolbar
# INSTALLED_APPS = INSTALLED_APPS + [
#     'debug_toolbar',
# ]
#
# MIDDLEWARE = MIDDLEWARE + [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    # 'default': {
    #     'BACKEND': 'django_redis.cache.RedisCache',
    #     'LOCATION': 'redis://127.0.0.1:6379',
    #     'OPTIONS': {
    #         'CLIENT_CLASS': 'django_redis.client.DefaultClient',
    #     },
    # },
}

INTERNAL_IPS = ('127.0.0.1')

try:
    from .local import *
except ImportError:
    pass

load_dotenv()

MAILCHIMP_API_KEY = os.getenv("MAILCHIMP_API_KEY")
MAILCHIMP_DATA_CENTER = os.getenv("MAILCHIMP_DATA_CENTER")
MAILCHIMP_NEWSLETTER_LIST_ID = os.getenv("MAILCHIMP_NEWSLETTER_LIST_ID")
