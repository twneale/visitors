#!/usr/bin/env python
from setuptools import setup, find_packages


long_description = ''

setup(name='visitors',
      version=0.1,
      packages=find_packages(),
      author='Thom Neale',
      author_email='twneale@gmail.com',
      license='BSD',
      url='http://github.com/twneale/visitors/',
      description='Basic visitor pattern implementation and extensions',
      long_description=long_description,
      platforms=['any'],
)
