from restthumbnails.helpers import get_secret, get_key


class ThumbnailBase(object):
    def __init__(self, source, size, method):
        self.source = source
        self.size = size
        self.method = method

    @property
    def size_string(self):
        return u'x'.join(map(str, self.size))

    @property
    def secret(self):
        return get_secret(self.source, self.size_string, self.method)

    @property
    def key(self):
        return get_key(self.source, self.size_string, self.method)
