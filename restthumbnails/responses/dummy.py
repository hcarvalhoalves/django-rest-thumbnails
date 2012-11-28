from django.conf import settings
from django.views.static import serve


def sendfile(request, thumbnail, **kwargs):
    from restthumbnails import defaults
    storage = defaults.storage_backend()
    return serve(request, thumbnail.name, storage.location)
