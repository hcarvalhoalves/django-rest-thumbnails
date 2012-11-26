from django.core.cache import cache
from django.core.files.storage import get_storage_class
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.template import Context

from restthumbnails.exceptions import ThumbnailError
from restthumbnails.helpers import get_thumbnail, get_thumbnail_proxy, get_key, get_secret
from restthumbnails.templatetags.thumbnail import thumbnail as thumbnail_tag

from models import ImageModel

import os


class StorageTestCase(TestCase):
    def setUp(self):
        from django.conf import settings
        self.storage = get_storage_class(getattr(settings,
            'REST_THUMBNAILS_STORAGE', None))()
        self.storage.cleanup()


class HelperTest(TestCase):
    def test_can_get_key(self):
        self.assertEqual(
            get_key('animals/kitten.jpg', '100x100', 'crop'),
            'restthumbnails-04c8f5c392a8d2b6ac86ad4e4c1dc5884a3ac317')


class ThumbnailTagTest(StorageTestCase):
    def setUp(self):
        super(ThumbnailTagTest, self).setUp()
        self.source_instance = ImageModel.objects.create(
            image='images/image.jpg')
        self.source = self.source_instance.image
        self.ctx = Context()

    def test_can_get_thumbnail_proxy_url(self):
        thumb = thumbnail_tag(self.ctx, self.source, '100x100', 'crop', '.jpg')
        self.assertIsNotNone(
            thumb)
        self.assertEquals(
            thumb.url,
            'http://example.com/images/image.jpg__100x100__crop.jpg')

    def test_raise_exception_on_invalid_parameters(self):
        self.assertRaises(
            ThumbnailError,
            thumbnail_tag, self.ctx, self.source, None, None, None)
        self.assertRaises(
            ThumbnailError,
            thumbnail_tag, self.ctx, self.source, 'foo', 'crop', '.jpg')
        self.assertRaises(
            ThumbnailError,
            thumbnail_tag, self.ctx, self.source, '200', 'crop', '.jpg')
        self.assertRaises(
            ThumbnailError,
            thumbnail_tag, self.ctx, self.source, '200 x 200', 'crop', '.jpg')
        self.assertRaises(
            ThumbnailError,
            thumbnail_tag, self.ctx, self.source, '200x200', 'foo', '.jpg')
        # self.assertRaises(
        #     ThumbnailError,
        #     thumbnail_tag, self.ctx, self.source, '200x200', 'crop', 'foo')


class ThumbnailViewTest(StorageTestCase):
    def setUp(self):
        super(ThumbnailViewTest, self).setUp()
        self.client = Client()

    def get(self, source, size, method, extension):
        url = '/%s__%s__%s%s' % (source, size, method, extension)
        return self.client.get(url)

    @override_settings(REST_THUMBNAILS_RESPONSE_BACKEND='restthumbnails.responses.nginx.sendfile')
    def test_nginx_headers(self):
        response = self.get('animals/kitten.jpg', '100x100', 'crop', '.jpg')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Accel-Redirect'], '/animals/kitten.jpg__100x100__crop.jpg')
        self.assertNotIn('Content-Type', response)

    @override_settings(REST_THUMBNAILS_RESPONSE_BACKEND='restthumbnails.responses.apache.sendfile')
    def test_apache_headers(self):
        response = self.get('animals/kitten.jpg', '100x100', 'crop', '.jpg')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Sendfile'], '/animals/kitten.jpg__100x100__crop.jpg')
        self.assertNotIn('Content-Type', response)

    def test_400_on_invalid_size(self):
        response = self.get('animals/kitten.jpg', 'derp', 'crop', '.jpg')
        self.assertEqual(
            response.status_code,
            400)

    def test_400_on_invalid_method(self):
        response = self.get('animals/kitten.jpg', '100x100', 'derp', '.jpg')
        self.assertEqual(
            response.status_code,
            400)


class ThumbnailFileTest(StorageTestCase):
    def thumbnail(self, source, size, method, extension, destination):
        thumb = get_thumbnail(source, size, method, extension)
        self.assertTrue(thumb.generate())
        self.assertTrue(self.storage.exists(destination))
        self.assertTrue(self.storage.size(destination) > 0)

    def test_can_crop(self):
        self.thumbnail(
            'animals/kitten.jpg', '100x100', 'crop', '.jpg',
            'animals/kitten.jpg__100x100__crop.jpg')

    def test_can_smart_crop(self):
        self.thumbnail(
            'animals/kitten.jpg', '100x100', 'smart', '.jpg',
            'animals/kitten.jpg__100x100__smart.jpg')

    def test_can_crop_on_width(self):
        self.thumbnail(
            'animals/kitten.jpg', '100x', 'crop', '.jpg',
            'animals/kitten.jpg__100x0__crop.jpg')

    def test_can_crop_on_height(self):
        self.thumbnail(
            'animals/kitten.jpg', 'x100', 'crop', '.jpg',
            'animals/kitten.jpg__0x100__crop.jpg')

    def test_can_upscale(self):
        self.thumbnail(
            'animals/kitten.jpg', '600x600', 'scale', '.jpg',
            'animals/kitten.jpg__600x600__scale.jpg')


class DummyImageTest(TestCase):
    @override_settings(REST_THUMBNAILS_THUMBNAIL_PROXY='restthumbnails.proxies.DummyImageProxy')
    def test_can_get_url(self):
        thumb = get_thumbnail_proxy('derp', '100x100', 'crop', '.jpg')
        self.assertEqual(
            thumb.url,
            'http://dummyimage.com/100x100')
