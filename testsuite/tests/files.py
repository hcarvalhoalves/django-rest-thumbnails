from restthumbnails.files import ThumbnailFile

from testsuite.tests.utils import StorageTestCase


class ThumbnailFileTestCase(StorageTestCase):
    def test_pil_can_identify_jpeg(self):
        thumb = ThumbnailFile(
            'pil_tests/1.jpg',
            '200x200',
            'crop',
            '.jpg')
        self.assertTrue(
            thumb.generate())
        thumb = ThumbnailFile(
            'pil_tests/2.jpg',
            '200x200',
            'crop',
            '.jpg')
        self.assertTrue(
            thumb.generate())
