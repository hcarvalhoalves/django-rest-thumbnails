from django.core.files.storage import FileSystemStorage
from django.conf import settings

import os
import shutil
import tempfile


class TemporaryStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        location = os.path.join(settings.MEDIA_ROOT, 'tmp/')
        base_url = os.path.join(settings.MEDIA_URL, 'tmp/')
        super(TemporaryStorage, self).__init__(
            location=location, base_url=base_url, *args, **kwargs)

    def cleanup(self):
        try:
            shutil.rmtree(self.base_location)
        except OSError:
            pass
