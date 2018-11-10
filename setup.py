#!/usr/bin/env python
import os
from django_imgur import version
from setuptools import setup


def get_packages():
    # setuptools can't do the job :(
    packages = []
    for root, dirnames, filenames in os.walk('django_imgur'):
        if '__init__.py' in filenames:
            packages.append(".".join(os.path.split(root)).strip("."))

    return packages


requires = ['imgurpython']


setup(
    name='django-imgur',
    version=version,
    description='A Django App that contains a Django '
    'Storage which uses Imgur.'
    'Inspired, based, and forked from django-dropbox',
    author=u'leonardo@perpli.me',
    url='https://github.com/leofiore/django-imgur',
    packages=get_packages(),
    install_requires=requires,
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
