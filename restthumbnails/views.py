from django import http
from django.core.cache import cache
from django.conf import settings
from django.views.generic import View
from django.utils.hashcompat import md5_constructor

from restthumbnails.exceptions import ThumbnailError
from restthumbnails.helpers import get_thumbnail

DEFAULT_TIMEOUT = 30

class ThumbnailView(View):
   def get(self, request, *args, **kwargs):
        # Return 400 on invalid parameters - HTTP agents should also
        # cache this response
        try:
            thumbnail = get_thumbnail(**self.kwargs)
        except ThumbnailError, e:
            return http.HttpResponseBadRequest(e)

        # Return 403 on untrusted requests - HTTP agents like Varnish
        # will cache this response, so this doubles as a rate limiter
        secret_param = getattr(settings,
            'REST_THUMBNAILS_SECRET_PARAM', 'secret')
        if request.GET.get(secret_param) != thumbnail.secret:
            return http.HttpResponseForbidden()

        # Make only one worker busy on this thumbnail by managing a lock
        if cache.get(thumbnail.key) is None:
            try:
                timeout = getattr(settings,
                    'REST_THUMBNAILS_LOCK_TIMEOUT', DEFAULT_TIMEOUT)
                cache.set(thumbnail.key, True, timeout)
                thumbnail.generate()
            finally:
                cache.delete(thumbnail.key)
            # Return 301 - HTTP agents will handle the load from now on
            return http.HttpResponsePermanentRedirect(thumbnail.url)
        # Return 404 while other workers have the lock
        raise http.Http404
