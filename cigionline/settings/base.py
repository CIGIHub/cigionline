"""
Django settings for cigionline project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from os import path

import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    'annual_reports',
    'articles',
    'careers',
    'compressor',
    'contact',
    'core',
    'embeds',
    'events',
    'features',
    'home',
    'images',
    'menus',
    'multimedia',
    'newsletters',
    'people',
    'promotions',
    'publications',
    'research',
    'robots',
    'search',
    'streams',
    'subscribe',
    'wagtailschedules',
    'signals',

    'wagtail.api.v2',
    'wagtail.contrib.forms',
    'wagtail.contrib.modeladmin',
    'wagtail.contrib.redirects',
    'wagtail.contrib.routable_page',
    'wagtail.contrib.table_block',
    'wagtail.contrib.styleguide',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',

    'modelcluster',
    'rest_framework',
    'taggit',
    'wagtailmedia',
    'webpack_loader',
    'adv_cache_tag',

    'wagtail_2fa',
    'django_otp',
    'django_otp.plugins.otp_totp',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'wagtail_2fa.middleware.VerifyUserMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

ROOT_URLCONF = 'cigionline.urls'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] ' +
                       'pathname=%(pathname)s lineno=%(lineno)s ' +
                       'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'cigionline': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': path.join(BASE_DIR, 'webpack-stats.json'),
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cigionline.wsgi.application'

simplecast_provider = {
    'endpoint': 'https://api.simplecast.com/oembed',
    'urls': [
        r'^https://(?:[-\w]+\.)?simplecast\.com/episodes/.+$',
    ]
}

WAGTAILEMBEDS_FINDERS = [
    {'class': 'embeds.finders.oembed.YouTubeOEmbedFinder'},
    {'class': 'wagtail.embeds.finders.oembed', 'providers': [simplecast_provider], },
    {'class': 'wagtail.embeds.finders.oembed', },
]

WAGTAILIMAGES_IMAGE_MODEL = 'images.CigionlineImage'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cigionline',
        'USER': 'cigi',
        'PASSWORD': 'cigi',
        'CONN_MAX_AGE': 600,
    }
}

if os.environ.get('GITHUB_WORKFLOW'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': 'localhost',
            'NAME': 'cigionline',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'CONN_MAX_AGE': 600,
        },
    }

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.elasticsearch7',
        'URLS': ['http://localhost:9200'],
        'INDEX': 'wagtail',
        'TIMEOUT': 30,
        'OPTIONS': {},
        'INDEX_SETTINGS': {
            'settings': {
                'index': {
                    'max_result_window': 13000,
                }
            }
        },
    },
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

ADV_CACHE_RESOLVE_NAME = True

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),

]

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# Javascript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/3.0/ref/contrib/staticfiles/#manifeststaticfilesstorage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'staticmedia')
MEDIA_URL = '/staticmedia/'


# Wagtail settings

WAGTAIL_SITE_NAME = "cigionline"
WAGTAILAPI_LIMIT_MAX = 40

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
WAGTAILADMIN_BASE_URL = 'https://edit.cigionline.org'

WAGTAIL_USER_TIME_ZONES = ['America/Toronto']
TIME_ZONE = 'America/Toronto'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Email settings
# NOTIFICATIONS_ON is a flag to determine whether notifications are sent in dev, staging, prod envs
if 'NOTIFICATIONS_ON' in os.environ:
    # if set to True, notifications are toggled on, sendgrid debug mode is set to false
    SENDGRID_SANDBOX_MODE_IN_DEBUG = not (os.environ['NOTIFICATIONS_ON'].lower() == "true")
else:
    # default to sandbox debug mode - will not send notifications
    SENDGRID_SANDBOX_MODE_IN_DEBUG = True
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
if 'SENDGRID_API_KEY' in os.environ:
    SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']
if 'PUBLISHING_NOTIFICATION_FROM_EMAIL' in os.environ:
    PUBLISHING_NOTIFICATION_FROM_EMAIL = os.environ['PUBLISHING_NOTIFICATION_FROM_EMAIL']
