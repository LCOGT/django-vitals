from django.conf import settings
from importlib import import_module


DEFAULT_CHECKS = [
    {
        'NAME': 'DatabaseCheck',
        'CLASS': 'vitals.checks.DatabaseCheck'
    },
    {
        'NAME': 'CacheCheck',
        'CLASS': 'vitals.checks.CacheCheck'
    },
    {
        'NAME': 'StorageCheck',
        'CLASS': 'vitals.checks.StorageCheck'
    }
]


def import_string(val):
    try:
        parts = val.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        msg = 'Could not import "{}"'.format(val)
        raise ImportError(msg)


class Settings(object):
    @property
    def enabled_checks(self):
        imports = getattr(settings, 'VITALS_ENABLED_CHECKS', DEFAULT_CHECKS)
        checks = {}
        for i in imports:
            checks[i['NAME']] = {
                'class': import_string(i['CLASS']),
                'args': i.get('OPTIONS', {})
            }
        return checks


conf = Settings()
