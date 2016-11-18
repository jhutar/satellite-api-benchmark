#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='satellite_api_benchmark',
      version='0.1',
      description='Red Hat Satellite API benchmark',
      long_description=readme(),
      classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
      ],
      keywords='performance',
      url='TODO',
      author='Jan Hutar',
      author_email='jhutar@redhat.com',
      license='GPLv3+',
      packages=['satellite_api_benchmark'],
      install_requires=['tabulate'],
      include_package_data=True,
      zip_safe=False)
