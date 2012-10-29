from django.conf import settings
from django.utils.importlib import import_module
from django.utils.hashcompat import md5_constructor

from restthumbnails import exceptions

import re

DEFAULT_KEY_PREFIX = 'restthumbnails'
DEFAULT_THUMBNAIL_FILE = 'restthumbnails.files.ThumbnailFile'
DEFAULT_THUMBNAIL_PROXY = 'restthumbnails.proxies.ThumbnailProxy'

RE_SIZE = re.compile(r'(\d+)?x(\d+)?$')


def _import_class(cls_path):
    package, name = cls_path.rsplit('.', 1)
    return getattr(import_module(package), name)


def get_secret(source, size, method):
    """
    Get a unique hash based on file path, size, method and SECRET_KEY.
    """
    secret_sauce = '-'.join((
        source, size, method, settings.SECRET_KEY))
    return md5_constructor(secret_sauce).hexdigest()


def get_key(source, size, method):
    """
    Get a unique key suitable for the cache backend.
    """
    prefix = getattr(settings, 'REST_THUMBNAILS_KEY_PREFIX', DEFAULT_KEY_PREFIX)
    return '-'.join((prefix, get_secret(source, size, method)))


def parse_size(size):
    """
    Parse a string in the format "[X]x[Y]" and return the dimensions as a tuple
    of numbers (or None if number is missing).

    >>> parse_size("200x200")
    (200, 200)
    >>> parse_size("200x")
    (200, 0)
    >>> parse_size("x200")
    (0, 200)
    """
    match = RE_SIZE.match(str(size))
    if not match or not any(match.groups()):
        raise exceptions.InvalidThumbnailSizeError("%s is not a valid size string." % size)
    return map(lambda x: 0 if not x else int(x), match.groups())


def parse_method(method):
    if method not in ['crop', 'smart', 'scale']:
        raise exceptions.InvalidThumbnailMethodError("%s is not a valid method string." % method)
    return method


def get_thumbnail(source, size, method):
    """
    Get a REST_THUMBNAILS_THUMBNAIL_FILE instance.
    """
    cls_path = getattr(settings, 'REST_THUMBNAILS_THUMBNAIL_FILE', DEFAULT_THUMBNAIL_FILE)
    return _import_class(cls_path)(source, parse_size(size), parse_method(method))


def get_thumbnail_proxy(source, size, method):
    """
    Get a REST_THUMBNAILS_THUMBNAIL_PROXY instance.
    """
    cls_path = getattr(settings, 'REST_THUMBNAILS_THUMBNAIL_PROXY', DEFAULT_THUMBNAIL_PROXY)
    return _import_class(cls_path)(source, parse_size(size), parse_method(method))
