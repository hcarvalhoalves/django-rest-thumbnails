class ThumbnailError(Exception):
    status = 400


class InvalidSizeError(ThumbnailError):
    pass


class InvalidMethodError(ThumbnailError):
    pass


class InvalidSecretError(ThumbnailError):
    status = 401


class SourceDoesNotExist(ThumbnailError):
    status = 404
