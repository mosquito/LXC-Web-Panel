#!/usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import, print_function
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


__version__ = '0.2-pre2'
__author__ = 'Élie Deloumeau, Antoine Tanzilli'


supports = {
    'install_requires': [
        'flask==0.9',
        'arconfig',
        'object_cacher',
    ]
}

data_files = []
if not os.path.exists('/var/lib/lxc/lwp.db'):
    data_files.append(('/var/lib/lxc/', ['resources/lwp.db']))

setup(
    name='lwp',
    version=__version__,
    author=__author__,
    license="MIT",
    description="LXC Web Interface",
    platforms="linux",
    classifiers=[
        'Environment :: Console',
        'Programming Language :: Python',
    ],
    scripts=['bin/lwp'],
    include_package_data=True,
    zip_safe=False,
    data_files=data_files,
    packages=find_packages(),
    **supports
)
