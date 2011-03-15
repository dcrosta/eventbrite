#!/usr/bin/env python

from setuptools import setup

from eventbrite import __version__ as version

setup(
    name = 'eventbrite',
    version = version,
    author = 'Matthew Tai',
    author_email = 'mtai84@gmail.com',
    description = "Client for Eventbrite's HTTP-based API",
    long_description=open('README.txt').read(),
    url = 'http://github.com/mtai/eventbrite/',
    packages = ['eventbrite'],
    license='Apache',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
