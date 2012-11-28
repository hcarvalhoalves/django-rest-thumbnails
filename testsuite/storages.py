from django.core.files.storage import FileSystemStorage
from django.conf import settings

import os
import shutil
import tempfile


class TemporaryStorage(FileSystemStorage):
    def cleanup(self):
        try:
            shutil.rmtree(self.location)
        except OSError:
            pass
