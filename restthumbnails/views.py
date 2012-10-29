from django.core.cache import cache
from django.conf import settings
from django.http import Http404, HttpResponsePermanentRedirect
from django.views.generic import View
from django.utils.hashcompat import md5_constructor

from restthumbnails.helpers import get_thumbnail, to_key
from restthumbnails.settings import LOCK_TIMEOUT


class ThumbnailView(View):
   def get(self, request, *args, **kwargs):
        key = to_key(**self.kwargs)
        thumbnail = get_thumbnail(**self.kwargs)
        # Make sure only one worker spends time generating the
        # thumbnail by managing a lock
        if cache.get(key) is None:
            try:
                cache.set(key, True, LOCK_TIMEOUT)
                thumbnail.generate()
            finally:
                cache.delete(key)
            # Return 301 and let the HTTP layer handle the load
            # from now on
            return HttpResponsePermanentRedirect(thumbnail.url)
        # Return 404 while other workers have the lock
        raise Http404
