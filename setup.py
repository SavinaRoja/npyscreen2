#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os


def long_description():
    readme = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(readme, 'r') as inf:
        readme_text = inf.read()
    return(readme_text)

setup(name='npyscreen2',
      version='0.0.1',
      description='npyscreen rebooted',
      long_description=long_description(),
      author='Paul Barton',
      author_email='pablo.barton@gmail.com',
      url='https://github.com/SavinaRoja',
      packages=['npyscreen2'],
      license='http://www.gnu.org/licenses/gpl-3.0.html',
      keywords='npyscreen,',
)
