import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = True

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(ROOT_DIR, 'media')

TEMPLATE_DIRS = [os.path.join(ROOT_DIR, 'templates')]

ROOT_URLCONF = 'testsuite.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'restthumbnails',
    'testsuite')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class':'logging.StreamHandler',
            'level':'DEBUG',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

#REST_THUMBNAILS_RESPONSE_BACKEND = 'restthumbnails.responses.nginx.sendfile'
#REST_THUMBNAILS_RESPONSE_BACKEND = 'restthumbnails.responses.apache.sendfile'

REST_THUMBNAILS_SOURCE_STORAGE_LOCATION = MEDIA_ROOT

REST_THUMBNAILS_STORAGE_BACKEND = 'testsuite.storages.TemporaryStorage'
REST_THUMBNAILS_STORAGE_LOCATION = os.path.join(MEDIA_ROOT, '..', 'tmp')
