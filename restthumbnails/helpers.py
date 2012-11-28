from django.conf import settings
from django.utils.crypto import salted_hmac

from restthumbnails import exceptions

import re


RE_SIZE = re.compile(r'(\d+)?x(\d+)?$')


def parse_size(size):
    """
    Parse a string in the format "[X]x[Y]" and return the dimensions as a tuple
    of integers. Raise InvalidSizeError if the string is not valid.

    >>> parse_size("200x200")
    (200, 200)
    >>> parse_size("200x")
    (200, 0)
    >>> parse_size("x200")
    (0, 200)
    """
    match = RE_SIZE.match(str(size))
    if not match or not any(match.groups()):
        raise exceptions.InvalidSizeError(
            "'%s' is not a valid size string." % size)
    return map(lambda x: 0 if not x else int(x), match.groups())


def parse_method(method):
    # FIXME: available processors should be a setting
    if method not in ['crop', 'smart', 'scale']:
        raise exceptions.InvalidMethodError(
            "'%s' is not a valid method string." % method)
    return method


def get_secret(source, size, method, extension):
    """
    Get a unique hash based on file path, size, method and SECRET_KEY.
    """
    secret_sauce = '-'.join((source, size, method, extension))
    return salted_hmac(source, secret_sauce).hexdigest()


def get_key(source, size, method, extension):
    """
    Get a unique key suitable for the cache backend.
    """
    from restthumbnails import defaults
    return '-'.join((
        defaults.KEY_PREFIX, get_secret(source, size, method, extension)))


def get_thumbnail(source, size, method, extension, secret):
    from restthumbnails import defaults
    instance = defaults.thumbnail_file()(
        source=source,
        size=size,
        method=method,
        extension=extension)
    if instance.secret != secret:
        raise exceptions.InvalidSecretError(
            "Secret '%s' does not match." % secret)
    return instance


def get_thumbnail_proxy(source, size, method, extension):
    from restthumbnails import defaults
    return defaults.thumbnail_proxy()(
        source=source,
        size=size,
        method=method,
        extension=extension)
