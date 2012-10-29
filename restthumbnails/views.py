from django import http
from django.core.cache import cache
from django.conf import settings
from django.views.generic import View
from django.utils.hashcompat import md5_constructor

from restthumbnails.exceptions import ThumbnailError
from restthumbnails.helpers import get_thumbnail, to_key, to_hash
from restthumbnails.settings import LOCK_TIMEOUT


class ThumbnailView(View):
   def get(self, request, *args, **kwargs):
        # Return 403 on untrusted requests - HTTP agents like Varnish
        # will cache this response, so this doubles as a rate limiter
        if request.GET.get('secret') != to_hash(**self.kwargs):
            return http.HttpResponseForbidden()

        # Return 400 on invalid parameters - HTTP agents should also
        # cache this response
        try:
            thumbnail = get_thumbnail(**self.kwargs)
        except ThumbnailError, e:
            return http.HttpResponseBadRequest(e)

        # Make only one worker busy on this thumbnail by managing a lock
        key = to_key(**self.kwargs)
        if cache.get(key) is None:
            try:
                cache.set(key, True, LOCK_TIMEOUT)
                thumbnail.generate()
            finally:
                cache.delete(key)
            # Return 301 - HTTP agents will handle the load from now on
            return http.HttpResponsePermanentRedirect(thumbnail.url)
        # Return 404 while other workers have the lock
        raise http.Http404
