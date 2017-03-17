from django.db import connections
from django.conf import settings
from django.core.cache import caches
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import requests


class BaseHealthCheck(object):
    def __init__(self, *args, **kwargs):
        self.name = kwargs['name']
        self.errors = []

    def check(self):
        raise NotImplementedError('Must implement check() method')

    def add_error(self, message):
        self.errors.append(message)

    def run_check(self):
        try:
            self.check()
        except Exception as exc:
            self.add_error('Unexpected exception: {}'.format(exc))


class DatabaseCheck(BaseHealthCheck):
    def check(self):
        for db in settings.DATABASES:
            try:
                connections[db].introspection.table_names()
            except Exception as exc:
                self.add_error('Could not connect to {}: {}'.format(db, exc))


class CacheCheck(BaseHealthCheck):
    def check(self):
        for cache in settings.CACHES:
            try:
                inst = caches[cache]
                inst.set('vitals_health_check', 1)
                assert inst.get('vitals_health_check') == 1, 'Data mismatch'
                inst.delete('vitals_health_check')
            except Exception as exc:
                self.add_error('Cache set failed on {}: {}'.format(cache, exc))


class StorageCheck(BaseHealthCheck):
    def check(self):
        try:
            path = default_storage.save('vitals_test', ContentFile(b'.'))
            assert default_storage.open(path).read() == b'.', 'Data mismatch'
            default_storage.delete(path)
            assert not default_storage.exists(path), 'Data still exists'
        except Exception as exc:
            self.add_error('Could not write test file: {}'.format(exc))


class HTTPCheck(BaseHealthCheck):
    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url')
        super(HTTPCheck, self).__init__(*args, **kwargs)

    def check(self):
        try:
            requests.get(self.url).raise_for_status()
        except Exception as exc:
            self.add_error('Endpoint {} unreachable: {}'.format(self.url, exc))
