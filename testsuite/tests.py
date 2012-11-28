from django.core.cache import cache
from django.core.files.storage import get_storage_class
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.template import Context

from restthumbnails import defaults, helpers, exceptions
from restthumbnails.templatetags.thumbnail import thumbnail as thumbnail_tag
from restthumbnails.proxies import ThumbnailProxy

from models import ImageModel

import os


class StorageTestCase(TestCase):
    def setUp(self):
        from django.conf import settings
        self.storage = get_storage_class(getattr(settings,
            'REST_THUMBNAILS_STORAGE', None))()
        self.storage.cleanup()


class HelperTest(TestCase):
    def setUp(self):
        self.params = {
            'source': 'animals/kitten.jpg',
            'size': '100x100',
            'method': 'crop',
            'extension': '.jpg',
        }

    def test_can_get_secret(self):
        self.assertEqual(
            helpers.get_secret(**self.params),
            '534790445e822052a0850de28544e19065425700')

    def test_can_get_key(self):
        self.assertEqual(
            helpers.get_key(**self.params),
            'restthumbnails-534790445e822052a0850de28544e19065425700')


class ThumbnailTagTest(StorageTestCase):
    def setUp(self):
        super(ThumbnailTagTest, self).setUp()
        self.source_instance = ImageModel.objects.create(
            image='images/image.jpg')
        self.source = self.source_instance.image
        self.ctx = Context()

    def test_can_get_thumbnail_proxy_url(self):
        thumb = thumbnail_tag(
            context=self.ctx,
            source=self.source,
            size='100x100',
            method='crop',
            extension='.jpg')
        self.assertIsNotNone(
            thumb)
        self.assertEquals(
            thumb.url,
            'http://example.com/images/image.jpg/100x100/crop/2c72090b2311c8d1eeeef881ce734f6f808193a0.jpg')

    def test_raise_exception_on_invalid_parameters(self):
        self.assertRaises(
            exceptions.ThumbnailError,
            thumbnail_tag, self.ctx, self.source, None, None, None)
        self.assertRaises(
            exceptions.ThumbnailError,
            thumbnail_tag, self.ctx, self.source, 'foo', 'crop', '.jpg')
        self.assertRaises(
            exceptions.ThumbnailError,
            thumbnail_tag, self.ctx, self.source, '200', 'crop', '.jpg')
        self.assertRaises(
            exceptions.ThumbnailError,
            thumbnail_tag, self.ctx, self.source, '200 x 200', 'crop', '.jpg')
        self.assertRaises(
            exceptions.ThumbnailError,
            thumbnail_tag, self.ctx, self.source, '200x200', 'foo', '.jpg')
        # self.assertRaises(
        #     exceptions.ThumbnailError,
        #     thumbnail_tag, self.ctx, self.source, '200x200', 'crop', 'foo')


class ThumbnailViewTest(StorageTestCase):
    def setUp(self):
        super(ThumbnailViewTest, self).setUp()
        self.client = Client()

    def get(self, **kwargs):
        from django.conf import settings
        base_url = getattr(settings,
            'REST_THUMBNAILS_BASE_URL', defaults.DEFAULT_BASE_URL)
        file_signature = getattr(settings,
            'REST_THUMBNAILS_FILE_SIGNATURE', defaults.DEFAULT_FILE_SIGNATURE)
        if 'secret' not in kwargs:
            kwargs['secret'] = helpers.get_secret(**kwargs)
        url = base_url + (file_signature % kwargs)
        return self.client.get(url)

    @override_settings(REST_THUMBNAILS_RESPONSE_BACKEND='restthumbnails.responses.nginx.sendfile')
    def test_nginx_headers(self):
        response = self.get(
            source='animals/kitten.jpg',
            size='100x100',
            method='crop',
            extension='.jpg')
        self.assertEqual(
            response.status_code,
            200)
        self.assertEqual(
            response['X-Accel-Redirect'],
            '/animals/kitten.jpg/100x100/crop/534790445e822052a0850de28544e19065425700.jpg')
        self.assertNotIn(
            'Content-Type',
            response)

    @override_settings(REST_THUMBNAILS_RESPONSE_BACKEND='restthumbnails.responses.apache.sendfile')
    def test_apache_headers(self):
        response = self.get(
            source='animals/kitten.jpg',
            size='100x100',
            method='crop',
            extension='.jpg')
        self.assertEqual(
            response.status_code,
            200)
        self.assertEqual(
            response['X-Sendfile'],
            '/animals/kitten.jpg/100x100/crop/534790445e822052a0850de28544e19065425700.jpg')
        self.assertNotIn(
            'Content-Type', response)

    def test_401_on_invalid_secret(self):
        response = self.get(
            source='animals/kitten.jpg',
            size='100x100',
            method='crop',
            extension='.jpg',
            secret='derp')
        self.assertEqual(
            response.status_code,
            401)

    def test_400_on_invalid_size(self):
        response = self.get(
            source='animals/kitten.jpg',
            size='derp',
            method='crop',
            extension='.jpg')
        self.assertEqual(
            response.status_code,
            400)

    def test_400_on_invalid_method(self):
        response = self.get(
            source='animals/kitten.jpg',
            size='100x100',
            method='derp',
            extension='.jpg')
        self.assertEqual(
            response.status_code,
            400)


class DummyImageTest(TestCase):
    @override_settings(REST_THUMBNAILS_THUMBNAIL_PROXY='restthumbnails.proxies.DummyImageProxy')
    def test_can_get_url(self):
        thumb = helpers.get_thumbnail_proxy(
            'dummy', '100x100', 'crop', '.jpg')
        self.assertEqual(
            thumb.url,
            'http://dummyimage.com/100x100')
