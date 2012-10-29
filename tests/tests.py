from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import get_storage_class
from django.test import TestCase
from django.test.client import Client
from django.template import Context

from restthumbnails.helpers import get_thumbnail, to_key, InvalidThumbnailError
from restthumbnails.templatetags.thumbnail import thumbnail as thumbnail_tag

from models import ImageModel

import os


class TemporaryFileTestCase(TestCase):
    def setUp(self):
        self.storage = get_storage_class(settings.REST_THUMBNAILS_STORAGE)()

    def tearDown(self):
        self.storage.cleanup()


class HelperTest(TestCase):
    def test_can_get_key(self):
        self.assertEqual(
            to_key('animals/kitten.jpg', '100x100', 'crop'),
            'restthumbnails-c28b868ea11dffe3b05e57c1c001e23c')


class ThumbnailTagTest(TemporaryFileTestCase):
    def setUp(self):
        super(ThumbnailTagTest, self).setUp()
        self.source_instance = ImageModel.objects.create(
            image='images/image.jpg')
        self.source = self.source_instance.image
        self.ctx = Context()

    def test_can_get_thumbnail_url(self):
        thumb = thumbnail_tag(self.ctx, self.source, '100x100', 'crop')
        self.assertIsNotNone(
            thumb)
        self.assertEquals(
            thumb.name,
            'images/image_100x100_crop.jpg')
        self.assertEquals(
            thumb.path,
            os.path.join(settings.MEDIA_ROOT, 'tmp/images/image_100x100_crop.jpg'))
        self.assertEquals(
            thumb.url,
            os.path.join(settings.MEDIA_URL, 'tmp/images/image_100x100_crop.jpg'))

    def test_raise_exception_on_invalid_parameters(self):
        self.assertRaises(
            InvalidThumbnailError,
            thumbnail_tag, self.ctx, self.source, None, None)
        self.assertRaises(
            InvalidThumbnailError,
            thumbnail_tag, self.ctx, self.source, 'foo', 'crop')
        self.assertRaises(
            InvalidThumbnailError,
            thumbnail_tag, self.ctx, self.source, '200', 'crop')
        self.assertRaises(
            InvalidThumbnailError,
            thumbnail_tag, self.ctx, self.source, '200 x 200', 'crop')
        self.assertRaises(
            InvalidThumbnailError,
            thumbnail_tag, self.ctx, self.source, '200x200', 'foo')


class ThumbnailViewTest(TemporaryFileTestCase):
    def setUp(self):
        super(ThumbnailViewTest, self).setUp()
        self.client = Client()
        self.path = 'animals/kitten.jpg'
        self.size = '100x100'
        self.method = 'crop'
        self.request_url = '/t/%s/%s/%s/' % (self.path, self.size, self.method)

    def test_redirect_after_get(self):
        response = self.client.get(self.request_url)
        self.assertRedirects(
            response,
            'http://mediaserver/media/tmp/animals/kitten_100x100_crop.jpg',
            status_code=301)


class ThumbnailFileTest(TemporaryFileTestCase):
    def test_can_crop_thumbnail(self):
        thumb = get_thumbnail('animals/kitten.jpg', '100x100', 'crop')
        self.assertTrue(thumb.generate())

    def test_can_smart_crop_thumbnail(self):
        thumb = get_thumbnail('animals/kitten.jpg', '100x100', 'smart')
        self.assertTrue(thumb.generate())

    def test_can_crop_in_one_dimension(self):
        thumb = get_thumbnail('animals/kitten.jpg', 'x100', 'crop')
        self.assertTrue(thumb.generate())
        thumb = get_thumbnail('animals/kitten.jpg', '100x', 'crop')
        self.assertTrue(thumb.generate())

    def test_can_upscale(self):
        thumb = get_thumbnail('animals/kitten.jpg', 'x600', 'scale')
        self.assertTrue(thumb.generate())
        thumb = get_thumbnail('animals/kitten.jpg', '600x', 'scale')
        self.assertTrue(thumb.generate())
