#!/usr/bin/env python

from distutils.core import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='pyholster',
      version='0.0.1',
      description='Mailgun class for interaction with Mailgun API',
      author='Peter Somhorst',
      author_email='peter.somhorst@gmail.com',
      url='https://github.com/psomhorst/pyholster',
      install_requires=required)
