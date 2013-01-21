from django.utils.log import getLogger

from restthumbnails import processors, exceptions
from restthumbnails.base import ThumbnailBase

import os


logger = getLogger(__name__)


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
        return self._generate()


class ThumbnailFile(ThumbnailFileBase):
    """
    Manages the generation of thumbnails using the storage backends
    defined in settings.

    >>> thumb = ThumbnailFile('path/to/file.jpg', (200, 200), 'crop', '.jpg')
    >>> thumb.generate()
    True
    >>> thumb.url
    '/path/to/file.jpg/200x200/crop/<random_hash>.jpg'

    """
    def __init__(self, **kwargs):
        from restthumbnails import defaults
        self.storage = defaults.storage_backend()
        self.source_storage = defaults.source_storage_backend()
        super(ThumbnailFile, self).__init__(**kwargs)

    def _exists(self):
        return self.storage.exists(self.path)

    def _source_exists(self):
        return self.source_storage.exists(self.source)

    @property
    def name(self):
        return self.file_signature % {
            'source': os.path.normpath(self.source),
            'size': self.size_string,
            'method': self.method,
            'secret': self.secret,
            'extension': self.extension}

    @property
    def path(self):
        return self.storage.path(self.name)

    @property
    def url(self):
        return self.storage.url(self.name)

    def generate(self):
        if self._source_exists():
            if not self._exists():
                im = processors.get_image(self.source_storage.open(self.source))
                im = processors.scale_and_crop(im, self.size, self.method)
                im = processors.save_image(im)
                self.storage.save(self.name, im)
                return True
            return False
        raise exceptions.SourceDoesNotExist()
