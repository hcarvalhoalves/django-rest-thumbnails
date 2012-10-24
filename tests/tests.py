from django.conf import settings
from django.core.cache import cache
from django.test import TestCase
from django.test.client import Client
from django.template import Context

from restthumbnails.helpers import get_thumbnail, to_key, InvalidSizeError
from restthumbnails.templatetags.thumbnail import thumbnail as thumbnail_tag

from models import ImageModel

import os


class HelperTest(TestCase):
    def test_can_get_key(self):
        self.assertEqual(
            to_key('animals/kitten.jpg', '200x200'),
            'restthumbnails-9487d8c879450f0594b66b393827c121')


class ThumbnailTagTest(TestCase):
    def setUp(self):
        self.source_instance = ImageModel.objects.create(
            image='images/image.jpg')
        self.source = self.source_instance.image
        self.ctx = Context()

    def test_can_get_thumbnail_url(self):
        thumb = thumbnail_tag(self.ctx, self.source, "200x200")
        self.assertIsNotNone(
            thumb)
        self.assertEquals(
            thumb.name,
            'images/image_200x200.jpg')
        self.assertEquals(
            thumb.path,
            os.path.join(settings.MEDIA_ROOT, 'images/image_200x200.jpg'))
        self.assertEquals(
            thumb.url,
            os.path.join(settings.MEDIA_URL, 'images/image_200x200.jpg'))

    def test_fail_on_empty_size(self):
        self.assertRaises(
            InvalidSizeError,
            thumbnail_tag, self.ctx, self.source, None)

    def test_fail_on_invalid_string(self):
        self.assertRaises(
            InvalidSizeError,
            thumbnail_tag, self.ctx, self.source, "foobar")
        self.assertRaises(
            InvalidSizeError,
            thumbnail_tag, self.ctx, self.source, "200")
        self.assertRaises(
            InvalidSizeError,
            thumbnail_tag, self.ctx, self.source, "200 x 200")
        self.assertRaises(
            InvalidSizeError,
            thumbnail_tag, self.ctx, self.source, "x")


class ThumbnailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.path = 'animals/kitten.jpg'
        self.size = '200x200'
        self.request_url = '/t/%s/%s/' % (self.path, self.size)
        self._release_lock(self.path, self.size) # Release locks between tests

    def _acquire_lock(self, path, size):
        cache.set(to_key(path, size), True)

    def _release_lock(self, path, size):
        cache.delete(to_key(path, size))

    def test_redirect_after_get(self):
        response = self.client.get(self.request_url)
        self.assertRedirects(response, 'http://mediaserver/media/animals/kitten_200x200.jpg', status_code=301)

    def test_404_while_locked(self):
        # 404 after lock is acquired
        self._acquire_lock(self.path, self.size)
        response = self.client.get(self.request_url)
        self.assertEqual(response.status_code, 404)
        # 301 after lock is released
        self._release_lock(self.path, self.size)
        response = self.client.get(self.request_url)
        self.assertEqual(response.status_code, 301)
