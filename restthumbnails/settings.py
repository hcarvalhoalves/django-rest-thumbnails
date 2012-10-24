from django.conf import settings

KEY_PREFIX = getattr(settings, 'REST_THUMBNAILS_PREFIX', "restthumbnails")
LOCK_TIMEOUT = getattr(settings, 'REST_THUMBNAILS_LOCK_TIMEOUT', 30)
