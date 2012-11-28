from django.conf import settings
from django.views.static import serve


def sendfile(request, location, **kwargs):
    from restthumbnails import defaults
    storage = defaults.storage_backend
    return serve(request, location, storage.location)
