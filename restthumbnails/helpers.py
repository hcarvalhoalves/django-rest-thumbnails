from django.conf import settings
from django.utils.hashcompat import md5_constructor
from django.utils.importlib import import_module

from restthumbnails import exceptions
from restthumbnails.settings import KEY_PREFIX, SECRET_KEY, THUMBNAIL_CLASS
from restthumbnails.thumbnails import ThumbnailFile

import re

DEFAULT_KEY_PREFIX = 'restthumbnails'
DEFAULT_THUMBNAIL_CLASS = 'restthumbnails.thumbnails.ThumbnailFile'

RE_SIZE = re.compile(r'(\d+)?x(\d+)?$')


def parse_size(size):
    """
    Parse a string in the format "[X]x[Y]" and return the dimensions as a tuple
    of numbers (or None if number is missing).

    >>> parse_size("200x200")
    (200, 200)
    >>> parse_size("200x")
    (200, None)
    >>> parse_size("x200")
    (None, 200)
    """
    match = RE_SIZE.match(str(size))
    if not match or not any(match.groups()):
        raise exceptions.InvalidThumbnailSizeError("%s is not a valid size string." % size)
    return map(lambda x: 0 if not x else int(x), match.groups())


def parse_method(method):
    if method not in ['crop', 'smart', 'scale']:
        raise exceptions.InvalidThumbnailMethodError("%s is not a valid method string." % method)
    return method


def to_hash(source, size, method):
    """
    Get a unique hash based on file path, size, method and SECRET_KEY.
    """
    secret_sauce = '-'.join((source, size, method, settings.SECRET_KEY))
    return md5_constructor(secret_sauce).hexdigest()


def to_key(source, size, method):
    """
    Get a unique key suitable for the cache backend.
    """
    prefix = getattr(settings, 'REST_THUMBNAILS_KEY_PREFIX', DEFAULT_KEY_PREFIX)
    return '-'.join((prefix, to_hash(source, size, method)))


def get_thumbnail(source, size, method):
    """
    Get a REST_THUMBNAILS_CLASS instance from a source and size string.
    """
    klass_path = getattr(settings, 'REST_THUMBNAILS_THUMBNAIL_CLASS', DEFAULT_THUMBNAIL_CLASS)
    package, name = klass_path.rsplit('.', 1)
    klass = getattr(import_module(package), name)
    return klass(source, parse_size(size), parse_method(method))
