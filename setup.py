#!/usr/bin/env python

from setuptools import setup, find_packages
from yzsdk import VERSION

url = 'steinliber.github.io'
long_description = 'YouZan Python SDK'

setup(name='yzsdk',
      version=VERSION,
      description=long_description,
      maintainer='meng',
      maintainer_email='18657532086@163.com',
      url=url,
      long_description=long_description,
      install_requires=['requests', 'pytz', 'urllib'],
      packages=find_packages('.'),
      )
