from django.conf import settings
from django.utils.importlib import import_module
from django.utils.hashcompat import md5_constructor
from django.utils.crypto import salted_hmac

from restthumbnails import defaults, exceptions

import re


RE_SIZE = re.compile(r'(\d+)?x(\d+)?$')


def import_from_path(cls_path):
    package, name = cls_path.rsplit('.', 1)
    return getattr(import_module(package), name)


def get_secret(source, size, method):
    """
    Get a unique hash based on file path, size, method and SECRET_KEY.
    """
    secret_sauce = '-'.join((source, size, method))
    return salted_hmac(source, secret_sauce).hexdigest()


def get_key(source, size, method):
    """
    Get a unique key suitable for the cache backend.
    """
    prefix = getattr(settings,
        'REST_THUMBNAILS_KEY_PREFIX', defaults.DEFAULT_KEY_PREFIX)
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
        raise exceptions.InvalidThumbnailSizeError(
            "%s is not a valid size string." % size)
    return map(lambda x: 0 if not x else int(x), match.groups())


def parse_method(method):
    # FIXME: available processors should be a setting
    if method not in ['crop', 'smart', 'scale']:
        raise exceptions.InvalidThumbnailMethodError(
            "%s is not a valid method string." % method)
    return method


def get_thumbnail(source, size, method, extension):
    """
    Get a REST_THUMBNAILS_THUMBNAIL_FILE instance.
    """
    cls_path = getattr(settings,
        'REST_THUMBNAILS_THUMBNAIL_FILE', defaults.DEFAULT_THUMBNAIL_FILE)
    return import_from_path(cls_path)(
        source=source,
        size=parse_size(size),
        method=parse_method(method),
        extension=extension)


def get_thumbnail_proxy(source, size, method, extension):
    """
    Get a REST_THUMBNAILS_THUMBNAIL_PROXY instance.
    """
    cls_path = getattr(settings,
        'REST_THUMBNAILS_THUMBNAIL_PROXY', defaults.DEFAULT_THUMBNAIL_PROXY)
    return import_from_path(cls_path)(
        source=source,
        size=parse_size(size),
        method=parse_method(method),
        extension=extension)

