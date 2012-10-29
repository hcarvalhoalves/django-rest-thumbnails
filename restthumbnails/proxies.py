from django.conf import settings
from django.utils.encoding import filepath_to_uri

from restthumbnails.base import ThumbnailBase

import urllib
import urlparse
import os


class ThumbnailProxyBase(ThumbnailBase):
    def __init__(self, source, size, method):
        # FieldFile/ImageFieldFile instances have a `name` attribute
        # with the relative file path
        source = getattr(source, 'name', source)
        super(ThumbnailProxyBase, self).__init__(source, size, method)

    @property
    def url(self):
        raise NotImplementedError


class ThumbnailProxy(ThumbnailProxyBase):
    def __init__(self, source, size, method):
        super(ThumbnailProxy, self).__init__(source, size, method)
        self.base_url = getattr(settings,
            'REST_THUMBNAILS_BASE_URL', '/')
        self.view_url = getattr(settings,
            'REST_THUMBNAILS_VIEW_URL', 't/%(source)s/%(size)s/%(method)s/')

    @property
    def url(self):
        url = self.view_url % {
            'source': filepath_to_uri(self.source),
            'size': self.size_string,
            'method': self.method}
        qs = urllib.urlencode({
            'secret': self.secret})
        return '?'.join((
            urlparse.urljoin(self.base_url, url),
            qs))


class DummyImageProxy(ThumbnailBase):
    url_template = 'http://dummyimage.com/%(width)sx%(height)s'

    @property
    def url(self):
        return self.url_template % {
            'width': self.size[0] or self.size[1],
            'height': self.size[1]}
