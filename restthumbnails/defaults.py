DEFAULT_SOURCE_STORAGE = None

DEFAULT_STORAGE = None

DEFAULT_BASE_URL = '/'

DEFAULT_FILE_SIGNATURE = r"%(source)s__%(size)s__%(method)s%(extension)s"

DEFAULT_URL_REGEX = r"^%s$" % (DEFAULT_FILE_SIGNATURE % {
    'source': r'(?P<source>.+)',
    'size': r'(?P<size>.+)',
    'method': r'(?P<method>.+)',
    'extension': r'(?P<extension>\..+)',
})

DEFAULT_LOCK_TIMEOUT = 10

DEFAULT_KEY_PREFIX = 'restthumbnails'

DEFAULT_THUMBNAIL_FILE = 'restthumbnails.files.ThumbnailFile'

DEFAULT_THUMBNAIL_PROXY = 'restthumbnails.proxies.ThumbnailProxy'

DEFAULT_RESPONSE_BACKEND = 'restthumbnails.responses.dummy.sendfile'
