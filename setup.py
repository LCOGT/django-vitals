import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-vitals',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    license='GPLv3',
    description='A django app that provides health check endpoints for vital services.',
    url='https://github.com/LCOGT/django-vitals',
    author='Austin Riba',
    author_email='ariba@lcogt.net',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ],
    install_requires=[
        'requests',
        'django',
    ]
)
