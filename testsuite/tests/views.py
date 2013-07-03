from django.core.cache import cache
from django.test.client import Client
from django.test.utils import override_settings

from testsuite.tests.utils import StorageTestCase

import urlparse


class ResponseBackendTestBase(StorageTestCase):
    def setUp(self):
        super(ResponseBackendTestBase, self).setUp()
        self.client = Client()

    def get(self, **kwargs):
        from restthumbnails import defaults, helpers

        if 'secret' not in kwargs:
            kwargs['secret'] = helpers.get_secret(**kwargs)

        url = urlparse.urljoin(
            defaults.THUMBNAIL_PROXY_BASE_URL,
            defaults.FILE_SIGNATURE % kwargs)
        return self.client.get(url)


class DefaultBackendTest(object):
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


@override_settings(THUMBNAILS_RESPONSE_BACKEND='restthumbnails.responses.nginx.sendfile')
class NginxBackendTest(DefaultBackendTest, ResponseBackendTestBase):
    def test_response_headers(self):
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
            '/thumbnails/animals/kitten.jpg/100x100/crop/38cdd9ad3dda068a81ebd59c113039637c1c8d1d.jpg')
        self.assertNotIn(
            'Content-Type',
            response)


@override_settings(THUMBNAILS_RESPONSE_BACKEND='restthumbnails.responses.apache.sendfile')
class ApacheBackendTest(DefaultBackendTest, ResponseBackendTestBase):
    def test_response_headers(self):
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
            '/thumbnails/animals/kitten.jpg/100x100/crop/38cdd9ad3dda068a81ebd59c113039637c1c8d1d.jpg')
        self.assertNotIn(
            'Content-Type', response)
