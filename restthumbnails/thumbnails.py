from django.conf import settings
from django.core.files.images import ImageFile
from django.core.files.storage import get_storage_class
from django.db.models.fields.files import ImageFieldFile
from django.utils.encoding import filepath_to_uri

from restthumbnails.helpers import get_secret, get_key
from restthumbnails.settings import SOURCE_STORAGE, TARGET_STORAGE
from restthumbnails import processors

from urllib import urlencode

import urlparse
import os


class ThumbnailBase(object):
    def __init__(self, source, size, method):
        self.source = source
        self.size = size
        self.method = method

    @property
    def size_string(self):
        return u'x'.join(map(str, self.size))

    @property
    def secret(self):
        return get_secret(self.source, self.size_string, self.method)

    @property
    def key(self):
        return get_key(self.source, self.size_string, self.method)


class ThumbnailFileBase(ThumbnailBase):
    @property
    def name(self):
        raise NotImplementedError

    @property
    def path(self):
        raise NotImplementedError

    @property
    def url(self):
        raise NotImplementedError

    def generate(self):
        raise NotImplementedError


class ThumbnailFile(ThumbnailBase):
    def __init__(self, source, size, method):
        super(ThumbnailFile, self).__init__(source, size, method)
        self.source_storage = get_storage_class(getattr(
            settings, 'REST_THUMBNAILS_SOURCE_STORAGE', None))()
        self.storage = get_storage_class(getattr(
            settings, 'REST_THUMBNAILS_STORAGE', None))()

    def _generate_filename(self):
        fname, ext = os.path.splitext(os.path.basename(self.source))
        return u'%s_%s_%s%s' % (fname, self.size_string, self.method, ext)

    def _base_path(self):
        return os.path.normpath(os.path.dirname(self.source))

    @property
    def name(self):
        return os.path.join(self._base_path(), self._generate_filename())

    @property
    def path(self):
        return self.storage.path(self.name)

    @property
    def url(self):
        return self.storage.url(self.name)

    def exists(self):
        return self.storage.exists(self.path)

    def source_exists(self):
        return self.source_storage.exists(self.source)

    def generate(self):
        if self.exists():
            return True
        if self.source_exists():
            im = processors.get_image(self.source_storage.open(self.source))
            im = processors.scale_and_crop(im, self.size, self.method)
            im = processors.save_image(im)
            self.storage.save(self.name, im)
            return True
        return False


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
        qs = urlencode({
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
