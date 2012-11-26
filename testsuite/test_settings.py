from settings import *

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {},
    'loggers': {}
}

MEDIA_URL = 'http://example.com/'

REST_THUMBNAILS_BASE_URL = 'http://example.com/'

#REST_THUMBNAILS_RESPONSE_BACKEND = 'restthumbnails.responses.nginx.sendfile'
#REST_THUMBNAILS_RESPONSE_BACKEND = 'restthumbnails.responses.apache.sendfile'

REST_THUMBNAILS_STORAGE = 'testsuite.storages.TemporaryStorage'
