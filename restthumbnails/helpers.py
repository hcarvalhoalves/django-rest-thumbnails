from django.utils.hashcompat import md5_constructor

from restthumbnails.settings import KEY_PREFIX
from restthumbnails.thumbnails import ThumbnailFile

import re

RE_SIZE = re.compile(r'(\d+)?x(\d+)?$')


class InvalidSizeError(Exception):
    """
    Raised when size strings fail to match the format "[X]x[Y]".
    """
    pass


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
        raise InvalidSizeError("%s is not a valid size string." % size)
    return map(lambda x: None if not x else int(x), match.groups())


def to_key(path, size, prefix=KEY_PREFIX):
    """
    Get a unique key based on file path and prefix.

    >>> to_key("/animals/kitten/01_200x200.jpg")
    'restthumbnails-41c56d28bbd9365d4ab4f57f38ead6a3'
    """
    return '-'.join([prefix, md5_constructor(path + size).hexdigest()])


def get_thumbnail(source, size):
    """
    Get a ThumbnailFile instance from a source and size string.
    """
    return ThumbnailFile(source, parse_size(size))
