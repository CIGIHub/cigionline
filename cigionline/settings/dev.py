from .base import *  # noqa: F401,F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ADMIN_ENABLED = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'a%86$z=ubc$(fh7@eqli92u!0t03#q-bq3=_trv1nn2+a=_5$n'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

# Uncomment this to enable Django debug toolbar
# INSTALLED_APPS = INSTALLED_APPS + [
#     'debug_toolbar',
#     'template_profiler_panel',
# ]
#
# MIDDLEWARE = MIDDLEWARE + [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]
# DEBUG_TOOLBAR_PANELS = [
#     'debug_toolbar.panels.history.HistoryPanel',
#     'debug_toolbar.panels.versions.VersionsPanel',
#     'debug_toolbar.panels.timer.TimerPanel',
#     'debug_toolbar.panels.settings.SettingsPanel',
#     'debug_toolbar.panels.headers.HeadersPanel',
#     'debug_toolbar.panels.request.RequestPanel',
#     'debug_toolbar.panels.sql.SQLPanel',
#     'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#     'debug_toolbar.panels.templates.TemplatesPanel',
#     'debug_toolbar.panels.cache.CachePanel',
#     'debug_toolbar.panels.signals.SignalsPanel',
#     'debug_toolbar.panels.logging.LoggingPanel',
#     'debug_toolbar.panels.redirects.RedirectsPanel',
#     'debug_toolbar.panels.profiling.ProfilingPanel',
#     'template_profiler_panel.panels.template.TemplateProfilerPanel',
# ]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'cigionline',
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
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
