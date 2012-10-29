from django.core.files.images import ImageFile
from django.core.files.storage import get_storage_class
from django.db.models.fields.files import ImageFieldFile

from restthumbnails.settings import SOURCE_STORAGE, TARGET_STORAGE
from restthumbnails import processors

import os


class ThumbnailFile(object):
    def __init__(self, source, size, method):
        self.source = getattr(source, 'name', source)
        self.size = size
        self.method = method
        self.source_storage = get_storage_class(SOURCE_STORAGE)()
        self.storage = get_storage_class(TARGET_STORAGE)()

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
