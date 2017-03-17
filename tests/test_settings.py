DEBUG = True,
SECRET_KEY = 'supersecret'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.sqlite3',
    },
}
INSTALLED_APPS = [
    'vitals',
]
ROOT_URLCONF = 'vitals.urls'
