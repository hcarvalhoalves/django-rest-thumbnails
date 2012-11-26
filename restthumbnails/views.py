from django import http
from django.core.cache import cache
from django.conf import settings
from django.views.generic import View

from restthumbnails import defaults
from restthumbnails.exceptions import ThumbnailError
from restthumbnails.helpers import get_thumbnail, import_from_path


class ThumbnailView(View):
    def __init__(self, *args, **kwargs):
        self.lock_timeout = getattr(settings,
            'REST_THUMBNAILS_LOCK_TIMEOUT', defaults.DEFAULT_LOCK_TIMEOUT)
        self.response_backend = getattr(settings,
            'REST_THUMBNAILS_RESPONSE_BACKEND', defaults.DEFAULT_RESPONSE_BACKEND)
        self.sendfile = import_from_path(self.response_backend)
        super(ThumbnailView, self).__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Return 400 on invalid parameters
        try:
            thumbnail = get_thumbnail(**self.kwargs)
        except ThumbnailError, e:
            return http.HttpResponse(status=400, content=e)

        # Make only one worker busy on this thumbnail by managing a lock
        if cache.get(thumbnail.key) is None:
            cache.set(thumbnail.key, True, self.lock_timeout)
            if thumbnail.generate():
                cache.delete(thumbnail.key)
                # Internal redirect to the generated file
                return self.sendfile(request, thumbnail.url)

        # Return 404 while there's a lock
        return http.HttpResponse(status=404)
