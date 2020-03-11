import dj_database_url
import logging
import os
from .base import *

logger = logging.getLogger(__name__)

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
    logger.info('Setting DATABASE_URL:')
    logger.info(os.environ['DATABASE_URL'])
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
    logger.info(DATABASES)
