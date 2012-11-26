from django.conf import settings
from django.core.files.storage import get_storage_class
from django.utils.log import getLogger

from restthumbnails.base import ThumbnailBase
from restthumbnails import defaults, processors

import os
import time


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
        start = time.clock()
        generated = self._generate()
        elapsed = (time.clock() - start)
        if generated:
            logger.info('%s took %ss', self.name, elapsed)
        return generated

    def _generate(self):
        raise NotImplementedError


class ThumbnailFile(ThumbnailFileBase):
    """
    Manages the generation of thumbnails using the storage backends
    defined in settings.

    >>> thumb = ThumbnailFile('path/to/file.jpg', (200, 200), 'crop', '.jpg')
    >>> thumb.generate()
    True
    >>> thumb.url
    '/path/to/file.jpg__200x200__crop.jpg'

    """
    def __init__(self, source, size, method, extension):
        super(ThumbnailFile, self).__init__(source, size, method, extension)
        self.source_storage = get_storage_class(getattr(settings,
            'REST_THUMBNAILS_SOURCE_STORAGE', defaults.DEFAULT_SOURCE_STORAGE))()
        self.storage = get_storage_class(getattr(settings,
            'REST_THUMBNAILS_STORAGE', defaults.DEFAULT_STORAGE))()
        self.file_signature = getattr(settings,
            'REST_THUMBNAILS_FILE_SIGNATURE', defaults.DEFAULT_FILE_SIGNATURE)

    def _dirname(self):
        return os.path.normpath(os.path.dirname(self.source))

    def _basename(self):
        return self.file_signature % {
            'source': os.path.basename(self.source),
            'size': self.size_string,
            'method': self.method,
            'extension': self.extension}

    def _exists(self):
        return self.storage.exists(self.path)

    def _source_exists(self):
        return self.source_storage.exists(self.source)

    def _generate(self):
        if self._source_exists():
            if not self._exists():
                im = processors.get_image(self.source_storage.open(self.source))
                im = processors.scale_and_crop(im, self.size, self.method)
                im = processors.save_image(im)
                self.storage.save(self.name, im)
            return True
        return False

    @property
    def name(self):
        return os.path.join(self._dirname(), self._basename())

    @property
    def path(self):
        return self.storage.path(self.name)

    @property
    def url(self):
        return u'/%s' % self.name
