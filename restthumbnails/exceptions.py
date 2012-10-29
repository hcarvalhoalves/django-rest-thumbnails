class ThumbnailError(Exception):
    """
    Base class for all thumbnail related errors.
    """
    pass


class InvalidThumbnailSizeError(ThumbnailError):
    pass


class InvalidThumbnailMethodError(ThumbnailError):
    pass
