from django.conf import settings
from django.utils.importlib import import_module

from restthumbnails import helpers


class ThumbnailBase(object):
    """
    Abstract class used both by ThumbnailFile and ThumbnailProxy instances
    """
    def __init__(self, source, size, method, extension, **kwargs):
        from restthumbnails import defaults
        # FieldFile/ImageFieldFile instances have a `name` attribute
        # with the relative file path
        self.source = getattr(source, 'name', source)
        self.file_signature = defaults.FILE_SIGNATURE
        self.size = helpers.parse_size(size)
        self.method = helpers.parse_method(method)
        self.extension = extension

    @property
    def size_string(self):
        return u'x'.join(map(str, self.size))

    @property
    def secret(self):
        return helpers.get_secret(
            self.source, self.size_string, self.method, self.extension)

    @property
    def key(self):
        return helpers.get_key(
            self.source, self.size_string, self.method, self.extension)
