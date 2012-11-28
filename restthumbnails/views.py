from django import http
from django.core.cache import cache
from django.conf import settings
from django.views.decorators.cache import add_never_cache_headers
from django.views.generic import View

from restthumbnails import defaults
from restthumbnails.exceptions import ThumbnailError
from restthumbnails.helpers import get_thumbnail


class ThumbnailView(View):
    def __init__(self, *args, **kwargs):
        self.lock_timeout = defaults.LOCK_TIMEOUT
        self.sendfile = defaults.response_backend()
        super(ThumbnailView, self).__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Return appropriate status code on invalid requests
        try:
            thumbnail = get_thumbnail(**self.kwargs)
        except ThumbnailError, e:
            # FIXME: Handle SourceDoesNotExist with a different,
            # cacheable response to keep bogus URLs from hitting
            # the backend all the time.
            return http.HttpResponse(status=e.status, content=e)

        # Make only one worker busy on this thumbnail by managing a lock
        if cache.get(thumbnail.key) is None:
            try:
                cache.set(thumbnail.key, True, self.lock_timeout)
                thumbnail.generate()
            finally:
                cache.delete(thumbnail.key)
            # Internal redirect to the generated file
            return self.sendfile(request, thumbnail.url)

        # Return 404 while there's a lock. Also, make sure user agents and
        # proxies don't cache this intermediate response.
        response = http.HttpResponse(status=404)
        add_never_cache_headers(response)
        return response
