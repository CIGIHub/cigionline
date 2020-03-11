import dj_database_url
from .base import *

DEBUG = False

try:
    from .local import *
except ImportError:
    pass

DATABASES['default'] = dj_database_url.config(conn_max_age=600)
