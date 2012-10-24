from django.core.files.storage import default_storage
from django.core.files.base import File

import os


class ThumbnailFile(File):
    def __init__(self, source, size, storage=None):
        self.source = getattr(source, 'name', source)
        self.storage = storage or default_storage
        self.size = size

    def _generate_filename(self):
        fname, ext = os.path.splitext(os.path.basename(self.source))
        size = u'x'.join(map(str, self.size))
        return u'%s_%s%s' % (fname, size, ext)

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

    def generate(self):
        # NOOP
        if self.exists():
            return False
        return True
