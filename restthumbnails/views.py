from django import http
from django.core.cache import cache
from django.conf import settings
from django.views.generic import View
from django.utils.hashcompat import md5_constructor

from restthumbnails.exceptions import ThumbnailError
from restthumbnails.helpers import get_thumbnail

SECRET_PARAM = getattr(settings, 'REST_THUMBNAILS_SECRET_PARAM', 'secret')
TIMEOUT = getattr(settings, 'REST_THUMBNAILS_LOCK_TIMEOUT', 30)


def rescue(status=200):
    return http.HttpResponse(status=status)


class ThumbnailView(View):
   def get(self, request, *args, **kwargs):
        # Return 400 on invalid parameters
        try:
            thumbnail = get_thumbnail(**self.kwargs)
        except ThumbnailError, e:
            return rescue(status=400)

        # Return 403 on untrusted requests
        if request.GET.get(SECRET_PARAM, '') != thumbnail.secret:
            return rescue(status=403)

        # Make only one worker busy on this thumbnail by managing a lock
        if cache.get(thumbnail.key) is None:
            try:
                cache.set(thumbnail.key, True, TIMEOUT)
                thumbnail.generate()
            finally:
                cache.delete(thumbnail.key)
            # Return 301 - HTTP agents will handle the load from now on
            return http.HttpResponsePermanentRedirect(thumbnail.url)

        # Return 404 while other workers have the lock
        return rescue(status=400)
