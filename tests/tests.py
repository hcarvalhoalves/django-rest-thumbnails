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
        self.source_storage = get_storage_class(getattr(settings,
            'REST_THUMBNAILS_SOURCE_STORAGE', None))()
        self.storage = get_storage_class(getattr(settings,
            'REST_THUMBNAILS_STORAGE', None))()

    def tearDown(self):
        if hasattr(self.storage, 'cleanup'):
            self.storage.cleanup()


class HelperTest(TestCase):
    def test_can_get_key(self):
        self.assertEqual(
            get_key('animals/kitten.jpg', '100x100', 'crop'),
            'restthumbnails-3b7b81c69082660cdff44ee0b6e07c46')


class ThumbnailTagTest(StorageTestCase):
    def setUp(self):
        super(ThumbnailTagTest, self).setUp()
        self.source_instance = ImageModel.objects.create(
            image='images/image.jpg')
        self.source = self.source_instance.image
        self.ctx = Context()

    def test_can_get_thumbnail_proxy_url(self):
        thumb = thumbnail_tag(self.ctx, self.source, '100x100', 'crop')
        secret = get_secret(self.source.name, '100x100', 'crop')
        self.assertIsNotNone(
            thumb)
        self.assertEquals(
            thumb.url,
            'http://thumbnailserver/t/images/image.jpg/100x100/crop/?secret=%s' % secret)

    def test_raise_exception_on_invalid_parameters(self):
        self.assertRaises(
            ThumbnailError,
            thumbnail_tag, self.ctx, self.source, None, None)
        self.assertRaises(
            ThumbnailError,
            thumbnail_tag, self.ctx, self.source, 'foo', 'crop')
        self.assertRaises(
            ThumbnailError,
            thumbnail_tag, self.ctx, self.source, '200', 'crop')
        self.assertRaises(
            ThumbnailError,
            thumbnail_tag, self.ctx, self.source, '200 x 200', 'crop')
        self.assertRaises(
            ThumbnailError,
            thumbnail_tag, self.ctx, self.source, '200x200', 'foo')


class ThumbnailViewTest(StorageTestCase):
    def setUp(self):
        super(ThumbnailViewTest, self).setUp()
        self.client = Client()

    def get(self, source, size, method, secret=None):
        secret = secret or get_secret(source, size, method)
        url = '/t/%s/%s/%s/?secret=%s' % (source, size, method, secret)
        return self.client.get(url)

    def test_301_on_sucessful_get(self):
        response = self.get('animals/kitten.jpg', '100x100', 'crop')
        self.assertRedirects(
            response,
            'http://mediaserver/media/tmp/animals/kitten_100x100_crop.jpg',
            301)

    def test_301_then_404_on_invalid_path(self):
        response = self.get('derp.jpg', '100x100', 'crop')
        self.assertEqual(
            response.status_code,
            301,
            404)

    def test_400_on_invalid_size(self):
        response = self.get('animals/kitten.jpg', 'derp', 'crop')
        self.assertEqual(
            response.status_code,
            400)

    def test_400_on_invalid_method(self):
        response = self.get('animals/kitten.jpg', '100x100', 'derp')
        self.assertEqual(
            response.status_code,
            400)

    def test_403_on_invalid_secret(self):
        response = self.get('animals/kitten.jpg', '100x100', 'crop', secret='derp')
        self.assertEqual(
            response.status_code,
            403)


class ThumbnailFileTest(StorageTestCase):
    def test_can_crop(self):
        thumb = get_thumbnail('animals/kitten.jpg', '100x100', 'crop')
        self.assertTrue(thumb.generate())
        self.assertTrue(self.storage.exists('animals/kitten_100x100_crop.jpg'))

    def test_can_smart_crop(self):
        thumb = get_thumbnail('animals/kitten.jpg', '100x100', 'smart')
        self.assertTrue(thumb.generate())
        self.assertTrue(self.storage.exists('animals/kitten_100x100_smart.jpg'))

    def test_can_crop_on_width(self):
        thumb = get_thumbnail('animals/kitten.jpg', '100x', 'crop')
        self.assertTrue(thumb.generate())
        self.assertTrue(self.storage.exists('animals/kitten_100x0_crop.jpg'))

    def test_can_crop_on_height(self):
        thumb = get_thumbnail('animals/kitten.jpg', 'x100', 'crop')
        self.assertTrue(thumb.generate())
        self.assertTrue(self.storage.exists('animals/kitten_0x100_crop.jpg'))

    def test_can_upscale(self):
        thumb = get_thumbnail('animals/kitten.jpg', '600x600', 'scale')
        self.assertTrue(thumb.generate())
        self.assertTrue(self.storage.exists('animals/kitten_600x600_scale.jpg'))


class DummyImageTest(TestCase):
    @override_settings(REST_THUMBNAILS_THUMBNAIL_PROXY='restthumbnails.thumbnails.DummyImageProxy')
    def test_can_get_url(self):
        thumb = get_thumbnail_proxy('derp', '100x100', 'crop')
        self.assertEqual(
            thumb.url,
            'http://dummyimage.com/100x100')
