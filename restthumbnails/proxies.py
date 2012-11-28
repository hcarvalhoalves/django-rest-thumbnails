from django.conf import settings
from django.utils.encoding import filepath_to_uri

from restthumbnails.base import ThumbnailBase
from restthumbnails import defaults

import urllib
import urlparse
import os


class ThumbnailProxyBase(ThumbnailBase):
    @property
    def url(self):
        raise NotImplementedError


class ThumbnailProxy(ThumbnailProxyBase):
    """
    A convenience proxy class used on templates to access the thumbnail URL.

    >>> thumb = ThumbnailProxy('path/to/file.jpg', (200, 200), 'crop', '.jpg')
    >>> thumb.url
    '/path/to/file.jpg/200x200/crop/<random_hash>.jpg'

    """
    def __init__(self, **kwargs):
        super(ThumbnailProxy, self).__init__(**kwargs)
        self.base_url = getattr(settings,
            'REST_THUMBNAILS_BASE_URL', defaults.DEFAULT_BASE_URL)

    @property
    def url(self):
        url = self.file_signature % {
            'source': filepath_to_uri(self.source),
            'size': self.size_string,
            'method': self.method,
            'secret': self.secret,
            'extension': self.extension}
        return urlparse.urljoin(self.base_url, url)


class DummyImageProxy(ThumbnailBase):
    """
    A dummy proxy that always returns a URL from the dummyimage.com site.
    """
    url_template = 'http://dummyimage.com/%(width)sx%(height)s'

    @property
    def url(self):
        return self.url_template % {
            'width': self.size[0] or self.size[1],
            'height': self.size[1]}
