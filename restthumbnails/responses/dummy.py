from django.conf import settings
from django.views.static import serve

from restthumbnails.helpers import import_from_path


def sendfile(request, location, **kwargs):
    storage = import_from_path(getattr(
        settings, 'REST_THUMBNAILS_STORAGE', None))()
    return serve(request, location, storage.location)
