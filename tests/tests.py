from django.test import TestCase, modify_settings, override_settings
from django.core.files.storage import Storage
from unittest.mock import MagicMock, patch
from requests.exceptions import HTTPError

from vitals.conf import import_string, conf, DEFAULT_CHECKS
from vitals.checks import DatabaseCheck, CacheCheck, StorageCheck, HTTPCheck
from vitals.views import run_checks


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

    def test_database_check_passes(self):
        check = DatabaseCheck(name='TestCheck')
        check.run_check()
        self.assertFalse(check.errors)

    @override_settings(CACHES={
        'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}
    })
    def test_cache_check(self):
        check = CacheCheck(name='TestCacheCheck')
        check.run_check()
        self.assertIn('Data mismatch', check.errors[0])
        self.assertEqual(len(check.errors), 1)

    def test_cache_check_passes(self):
        check = CacheCheck(name='TestCacheCheck')
        check.run_check()
        self.assertFalse(check.errors)

    def test_storage_check(self):
        sm = MagicMock(spec=Storage, name='StorageMock')
        with patch('django.core.files.storage.default_storage._wrapped', sm):
            check = StorageCheck(name='TestStorageCheck')
            check.run_check()
            self.assertIn('Data mismatch', check.errors[0])
            self.assertEqual(len(check.errors), 1)

    def test_stoage_check_passes(self):
        check = StorageCheck(name='TestStorageCheck')
        check.run_check()
        self.assertFalse(check.errors)

    @patch('requests.get', side_effect=HTTPError)
    def test_http_check(self, get_mock):
        check = HTTPCheck(name='TestHTTPCheck', url='groogle.nom')
        check.run_check()
        self.assertIn('groogle.nom unreachable', check.errors[0])
        self.assertEqual(len(check.errors), 1)

    @patch('requests.get')
    def test_http_check_passes(self, get_mock):
        check = HTTPCheck(name='TestHTTPCheck', url='groogle.nom')
        check.run_check()
        self.assertFalse(check.errors)


class TestViews(TestCase):
    def test_run_checks(self):
        result = run_checks()
        self.assertEqual(len(result['ok']), len(DEFAULT_CHECKS))

    def test_run_single_check(self):
        result = run_checks(['DatabaseCheck'])
        self.assertEqual(len(result['ok']), 1)

    def test_run_multiple_checks(self):
        result = run_checks(['DatabaseCheck', 'CacheCheck'])
        self.assertEqual(len(result['ok']), 2)

    def test_run_checks_bad_check(self):
        with self.assertRaises(KeyError):
            run_checks(['notacheck'])

    def test_jsonview(self):
        result = self.client.get('/').json()
        self.assertEqual(len(result['ok']), len(DEFAULT_CHECKS))

    def test_jsonview_check_param(self):
        result = self.client.get('/?checks=DatabaseCheck').json()
        self.assertEqual(len(result['ok']), 1)
        self.assertEqual(result['ok'][0], 'DatabaseCheck')

    def test_jsonview_check_param_multiple(self):
        result = self.client.get('/?checks=DatabaseCheck,CacheCheck').json()
        self.assertEqual(len(result['ok']), 2)
        self.assertEqual(result['ok'], ['DatabaseCheck', 'CacheCheck'])
        self.assertNotIn('StorageCheck', result['ok'])
        self.assertNotIn('StorageCheck', result['failed'])
