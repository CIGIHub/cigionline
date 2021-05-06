from .production import *  # noqa: F401,F403

ADMIN_ENABLED = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'cigionline',
    },
}

CACHE_CONTROL_MAX_AGE = 0
