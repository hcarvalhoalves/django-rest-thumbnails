from settings import *

MEDIA_URL = 'http://mediaserver/media/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {},
    'loggers': {}
}

REST_THUMBNAILS_STORAGE = 'testsuite.storages.TemporaryStorage'

REST_THUMBNAILS_BASE_URL = 'http://testserver/t/'
