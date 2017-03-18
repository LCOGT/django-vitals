# django-vitals
A django app that provides health check endpoints for vital services.

[![Build Status](https://travis-ci.org/LCOGT/django-vitals.svg?branch=master)](https://travis-ci.org/LCOGT/django-vitals)
[![Coverage Status](https://coveralls.io/repos/github/LCOGT/django-vitals/badge.svg?branch=master)](https://coveralls.io/github/LCOGT/django-vitals?branch=master)

It is often useful to get the status of services from the perspective of the application that needs them.
django-vitals provides a simple mechanism for writing a running health checks. These checks can then be exposed
via an endpoint:

```json

{
    "ok": [
        "DatabaseCheck",
        "CacheCheck",
        "StorageCheck"
    ],
    "failed": {}
}
```
Which in the above case, would return a status code of `200`

If something is down:

```json
{
    "ok": [
        "DatabaseCheck",
        "CacheCheck",
        "StorageCheck"
    ],
    "failed": {
        "OtherMicroServiceEndpointCheck": [
            "Endpoint http://suchabadsite11112222.com unreachable: Failed to establish a new connection: [Errno -2] Name or service not known"
        ]
    }
}
```

a http code `500` is returned instead.

Subsets of checks can be run by passing the `check` parameter to the endpoint: `?checks=DatabaseCheck,CacheCheck`

This can be particularity useful when used along with load balancers, container orchestration and other
infrastructure tools that can take automatic actions when problems arise.

## Requirements
Tested with all combinations of:

* Python 3.4+
* Django 1.8+

Python 2.7 probably works, but I have no interest in testing it. Support will be on a best effort basis.

## Installation

Install the package from pypi:

    pip install django-vitals

Add `vitals` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = (
    ...
    'vitals'
    ...
)
```

Add `vitals.urls` to your urlconf:

```python
urlpatterns = [
    ...
    url(r'^healthz/', include('vitals.urls', namespace='vitals')),
    ...
]
```
Visit the url in your browser.

That's it if all you want is the default checks (`DatabaseCheck`, `CacheCheck`, `StorageCheck`)
`HTTPCheck` is included but not enabled by default.


## Configuration

By default 3 health checks are run: `DatabaseCheck`, `CacheCheck` and `StorageCheck`.
Add `VITALS_ENABLED_CHECKS` to your `settings.py` to customize:

```python
VITALS_ENABLED_CHECKS = [
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
    },
    {
        'NAME': 'HTTPCheck',
        'CLASS': 'vitals.checks.HTTPCheck',
        'OPTIONS': {
            'url': 'https://google.com'
        }
    }
]
```

## Included Checks

### DatabaseCheck
Options: None

Iterates over every database in `settings.DATABASES` and attempts to access the list of tables for each.

### CacheCheck
Options: None

Iterates over every cache in `settings.CACHES` and attempts to set a value, get it and remove it.

### StorageCheck
Options: None

Using the default storage backend, attempts to write a small file and delete it.

### HTTPCheck
Options: `url`

Attempts to GET the url provided by the `url` option. Will fail if the GET results in anything other than a `200` response code.

## Writing Custom Checks

You are not limited to the included health checks. To write a custom check, simply subclass `BaseHealthCheck`
and implement the `check()` method:

```python
from vitals.checks import BaseHealthCheck

class MyHealthCheck(BaseHealthCheck):
    def check(self):
        assert 2 == 2
```

Any exceptions thrown by your check will be added as errors. You can also manually add errors using `self.add_error(error)`:

```python
from vitals.checks import BaseHealthCheck

class MyHealthCheck(BaseHealthCheck):
    def check(self):
        try:
            assert 1 == 2
        except AssertionError as exc:
            self.add_error('Strange error! {}'.format(exc))
```

Arguments can be passed to health checks by setting the `OPTIONS` key in settings:

```python
VITALS_ENABLED_CHECKS = [
     {
        'NAME': 'MyFailingHealthCheck',
        'CLASS': 'foo.MyHealthCheck',
        'OPTIONS': {
            'number': 3
        }
    }
]
```

They will be passed a kwargs to your class constructor:

```python
from vitals.checks import BaseHealthCheck

class MyHealthCheck(BaseHealthCheck):
    def __init__(self, *args, **kwargs):
        self.number = kwargs.pop('number')
        super(MyHealthCheck, self).__init__(*args, **kwargs)

    def check(self):
        assert self.number == 2
```

Add your custom checks to `VITALS_ENABLED_CHECKS` in `settings.py` providing the path to them in the `CLASS` key.
