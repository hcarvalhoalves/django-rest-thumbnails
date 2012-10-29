from django.conf import settings
from django.core.files.images import ImageFile
from django.core.files.storage import get_storage_class
from django.db.models.fields.files import ImageFieldFile

from restthumbnails.settings import SOURCE_STORAGE, TARGET_STORAGE
from restthumbnails import processors

import os


class BaseThumbnailFile(object):
    def __init__(self, source, size, method):
        self.source = getattr(source, 'name', source)
        self.size = size
        self.method = method

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


class ThumbnailFile(BaseThumbnailFile):
    def __init__(self, source, size, method):
        super(ThumbnailFile, self).__init__(source, size, method)
        self.source_storage = get_storage_class(getattr(
            settings, 'REST_THUMBNAILS_SOURCE_STORAGE', None))()
        self.storage = get_storage_class(getattr(
            settings, 'REST_THUMBNAILS_STORAGE', None))()

    def _generate_filename(self):
        fname, ext = os.path.splitext(os.path.basename(self.source))
        size = u'x'.join(map(str, self.size))
        return u'%s_%s_%s%s' % (fname, size, self.method, ext)

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


class DummyThumbnailFile(BaseThumbnailFile):
    base_url = 'http://dummyimage.com/%(width)sx%(height)s'

    @property
    def name(self):
        return None

    @property
    def path(self):
        return None

    @property
    def url(self):
        options = {
            'width': self.size[0] or self.size[1],
            'height': self.size[1]}
        return self.base_url % options

    def generate(self):
        return True
