import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-vitals',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    license='GPLv2',
    description='A django app that provides health check endpoints for vital services.',
    url='https://github.com/LCOGT/django-vitals',
    author='Austin Riba',
    author_email='ariba@lcogt.net',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independant',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'TOPIC :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'requests',
        'django',
    ]
)
