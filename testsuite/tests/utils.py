from django.test import TestCase


class StorageTestCase(TestCase):
    def setUp(self):
        from restthumbnails import defaults
        self.storage = defaults.storage_backend()
        self.storage.cleanup()
