from django.utils.hashcompat import md5_constructor

from restthumbnails import exceptions
from restthumbnails.settings import KEY_PREFIX, SECRET_KEY
from restthumbnails.thumbnails import ThumbnailFile

import re

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


def to_hash(source, size, method, secret=SECRET_KEY):
    """
    Get a unique hash based on file path, size, method and secret key.
    """
    secret_sauce = '-'.join((source, size, method, secret))
    return md5_constructor(secret_sauce).hexdigest()


def to_key(source, size, method, prefix=KEY_PREFIX):
    """
    Get a unique key suitable for the cache backend.
    """
    return '-'.join((prefix, to_hash(source, size, method)))


def get_thumbnail(source, size, method):
    """
    Get a ThumbnailFile instance from a source and size string.
    """
    return ThumbnailFile(source, parse_size(size), parse_method(method))
