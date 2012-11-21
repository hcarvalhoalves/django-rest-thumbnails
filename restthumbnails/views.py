from django import http
from django.core.cache import cache
from django.conf import settings
from django.views.generic import View
from django.utils.hashcompat import md5_constructor
from django.utils.cache import patch_cache_control

from restthumbnails.exceptions import ThumbnailError
from restthumbnails.helpers import get_thumbnail

DEFAULT_RESPONSE_HEADERS = {
    'cache_control': 'public',
    'max_age': '3600',
}

def rescue(status=200, **kwargs):
    response = http.HttpResponse(status=status)
    patch_cache_control(response, **kwargs)
    return response


def redirect_to(redirect_to, **kwargs):
    response = http.HttpResponsePermanentRedirect(redirect_to)
    patch_cache_control(response, **kwargs)
    return response


class ThumbnailView(View):
    def __init__(self, *args, **kwargs):
        self.use_secret_param = getattr(settings, 'REST_THUMBNAILS_USE_SECRET_PARAM', True)
        self.secret_param = getattr(settings, 'REST_THUMBNAILS_SECRET_PARAM', 'secret')
        self.lock_timeout = getattr(settings, 'REST_THUMBNAILS_LOCK_TIMEOUT', 30)
        self.response_headers = getattr(settings, 'REST_THUMBNAILS_RESPONSE_HEADERS', DEFAULT_RESPONSE_HEADERS)
        super(ThumbnailView, self).__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Return 400 on invalid parameters
        try:
            thumbnail = get_thumbnail(**self.kwargs)
        except ThumbnailError, e:
            return rescue(400)

        # Return 403 on untrusted requests
        if self.use_secret_param and request.GET.get(self.secret_param, '') != thumbnail.secret:
            return rescue(403)

        # Make only one worker busy on this thumbnail by managing a lock
        if cache.get(thumbnail.key) is None:
            try:
                cache.set(thumbnail.key, True, self.lock_timeout)
                thumbnail.generate()
            finally:
                cache.delete(thumbnail.key)
            # Return 301 - HTTP agents will handle the load from now on
            return redirect_to(thumbnail.url, **self.response_headers)

        # Return 404 while other workers have the lock
        return rescue(400)
