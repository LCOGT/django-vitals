from django.test import TestCase, modify_settings, override_settings
from django.core.files.storage import Storage
from unittest.mock import MagicMock, patch
from requests.exceptions import HTTPError
import json

from vitals.conf import import_string, conf, DEFAULT_CHECKS
from vitals.checks import DatabaseCheck, CacheCheck, StorageCheck, HTTPCheck
from vitals.checks import BaseHealthCheck
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

    @patch('vitals.checks.CacheCheck.check', side_effect=Exception)
    def test_check_unexecpted_exception(self, mock_check):
        check = CacheCheck(name='TestCacheCheck')
        check.run_check()
        self.assertEqual(len(check.errors), 1)


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
        result = json.loads(str(self.client.get('/').content, encoding='utf8'))
        self.assertEqual(len(result['ok']), len(DEFAULT_CHECKS))

    def test_jsonview_check_param(self):
        response = self.client.get('/?checks=DatabaseCheck')
        result = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(len(result['ok']), 1)
        self.assertEqual(result['ok'][0], 'DatabaseCheck')

    def test_jsonview_check_param_multiple(self):
        response = self.client.get('/?checks=DatabaseCheck,CacheCheck')
        result = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(len(result['ok']), 2)
        self.assertEqual(result['ok'], ['DatabaseCheck', 'CacheCheck'])
        self.assertNotIn('StorageCheck', result['ok'])
        self.assertNotIn('StorageCheck', result['failed'])

    @patch('vitals.checks.CacheCheck.check', side_effect=Exception)
    def test_jsonview_check_fails(self, check_mock):
        response = self.client.get('/')
        result = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(len(result['failed']), 1)
        self.assertEqual(len(result['ok']), 2)
        self.assertEqual(response.status_code, 500)


class BadCheck(BaseHealthCheck):
    pass


class TestBadCheckImpl(TestCase):
    def test_check_has_no_check(self):
        bc = BadCheck(name='notgonnawork')
        bc.run_check()
        self.assertEqual(len(bc.errors), 1)
        self.assertIn('Must implement', bc.errors[0])
