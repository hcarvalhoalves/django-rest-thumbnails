import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

TEST_SETTINGS=dict(
    DEBUG=True,
    MEDIA_URL='http://mediaserver/media/',
    MEDIA_ROOT=os.path.join(ROOT_DIR, 'media'),
    TEMPLATE_DIRS=[os.path.join(ROOT_DIR, 'templates')],
    ROOT_URLCONF='tests.urls',
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'}},
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }},
    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.admin',
        'restthumbnails',
        'tests'),
    REST_THUMBNAILS_STORAGE='tests.storages.TemporaryStorage',
    REST_THUMBNAILS_BASE_URL='http://thumbnailserver/')
