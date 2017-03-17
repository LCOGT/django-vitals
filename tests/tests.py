from django.test import TestCase, modify_settings, override_settings
from django.core.files.storage import Storage
from unittest.mock import MagicMock, patch

from vitals.conf import import_string, conf, DEFAULT_CHECKS
from vitals.checks import DatabaseCheck, CacheCheck, StorageCheck


class TestConf(TestCase):
    def test_import_string(self):
        module = import_string('numbers.Number')
        self.assertTrue(isinstance(1, module))

    def test_bad_import(self):
        with self.assertRaises(ImportError):
            import_string('not.really.a.module')

    def test_settings_object(self):
        for check in DEFAULT_CHECKS:
            self.assertIn(check['NAME'], conf.enabled_checks.keys())


class TestChecks(TestCase):
    @modify_settings(DATABASES={'append': {'nonsense': {'ENGINE': 'nonsene'}}})
    def test_database_check(self):
        check = DatabaseCheck(name='TestCheck')
        check.run_check()
        self.assertIn('Could not connect', check.errors[0])
        self.assertEqual(len(check.errors), 1)

    @override_settings(CACHES={
        'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}
    })
    def test_cache_check(self):
        check = CacheCheck(name='TestCacheCheck')
        check.run_check()
        self.assertIn('Data mismatch', check.errors[0])
        self.assertEqual(len(check.errors), 1)

    def test_storage_check(self):
        sm = MagicMock(spec=Storage, name='StorageMock')
        with patch('django.core.files.storage.default_storage._wrapped', sm):
            check = StorageCheck(name='TestStorageCheck')
            check.run_check()
            self.assertIn('Data mismatch', check.errors[0])
            self.assertEqual(len(check.errors), 1)
