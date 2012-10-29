from django.conf import settings

KEY_PREFIX = getattr(settings, 'REST_THUMBNAILS_PREFIX', 'restthumbnails')

SECRET_KEY = getattr(settings, 'REST_THUMBNAILS_SECRET_KEY', settings.SECRET_KEY)

LOCK_TIMEOUT = getattr(settings, 'REST_THUMBNAILS_LOCK_TIMEOUT', 30)

SOURCE_STORAGE = getattr(settings, 'REST_THUMBNAILS_SOURCE_STORAGE', None)

TARGET_STORAGE = getattr(settings, 'REST_THUMBNAILS_STORAGE', None)
