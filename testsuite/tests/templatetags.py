from django.template import Context
from django.test.utils import override_settings

from restthumbnails import exceptions
from restthumbnails.templatetags.thumbnail import thumbnail as thumbnail_tag

from testsuite.models import ImageModel
from testsuite.tests.utils import StorageTestCase


class ThumbnailTagTestBase(object):
    def setUp(self):
        super(ThumbnailTagTestBase, self).setUp()
        self.source_instance = ImageModel.objects.create(image='images/image.jpg')
        self.source = self.source_instance.image
        self.ctx = Context()

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

    def test_none_on_empty_source(self):
        self.assertEqual(
            thumbnail_tag(self.ctx, '', '200x200', 'crop', '.jpg'),
            None)


@override_settings(THUMBNAILS_PROXY='restthumbnails.proxies.ThumbnailProxy')
class ThumbnailProxyTest(ThumbnailTagTestBase, StorageTestCase):
    def test_can_get_url(self):
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
            '/thumbnails/images/image.jpg/100x100/crop/72ebae3f7fcda69b79bbf1c55ebe22197100e06e.jpg')


@override_settings(THUMBNAILS_PROXY='restthumbnails.proxies.DummyImageProxy')
class DummyImageProxyTest(ThumbnailTagTestBase, StorageTestCase):
    def test_can_get_url(self):
        thumb = thumbnail_tag(
            context=self.ctx,
            source=self.source,
            size='100x100',
            method='crop',
            extension='.jpg')
        self.assertIsNotNone(
            thumb)
        self.assertEqual(
            thumb.url,
            'http://dummyimage.com/100x100')
