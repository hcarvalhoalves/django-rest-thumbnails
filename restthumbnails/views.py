from django.core.cache import cache
from django.conf import settings
from django.http import Http404, HttpResponsePermanentRedirect
from django.views.generic import View
from django.utils.hashcompat import md5_constructor

from restthumbnails.helpers import get_thumbnail, to_key
from restthumbnails.settings import LOCK_TIMEOUT


class ThumbnailView(View):
   def get(self, request, *args, **kwargs):
        path = self.kwargs['path']
        size = self.kwargs['size']

        key = to_key(path, size)
        thumbnail = get_thumbnail(path, size)

        # Check if any worker acquired a lock
        if cache.get(key) is None:
            try:
                cache.set(key, True, LOCK_TIMEOUT)
                thumbnail.generate()
            finally:
                cache.delete(key)
            # Return 301 after succesfully generating thumbnail
            return HttpResponsePermanentRedirect(thumbnail.url)
        # Return 404 while we have a lock
        raise Http404
