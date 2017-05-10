#!/usr/bin/env python

from setuptools import setup, find_packages
import re

url = 'steinliber.github.io'
long_description = 'YouZan Python SDK'

with open('yzsdk/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(name='yzsdk',
      version=version,
      description=long_description,
      maintainer='meng',
      maintainer_email='18657532086@163.com',
      url=url,
      long_description=long_description,
      install_requires=['requests', 'pytz'],
      packages=find_packages('.'),
      )
