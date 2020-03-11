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

DATABASES['default'] = dj_database_url.config(conn_max_age=600)
