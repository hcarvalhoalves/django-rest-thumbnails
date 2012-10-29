from django.conf import settings
from django.core.files.storage import get_storage_class

from restthumbnails.base import ThumbnailBase
from restthumbnails import processors

import os


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
    """
    Manages the generation of thumbnails using the storage backends
    defined in settings.

    >>> thumb = ThumbnailFile('path/to/file.jpg', (200, 200), 'crop')
    >>> thumb.generate()
    True
    >>> thumb.url
    '/media/path/to/file_200x200_crop.jpg'

    """
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
