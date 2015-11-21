#!/usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import, print_function
from setuptools import setup, find_packages
import lwp


REQUIREMENTS = [
    'tornado>=4.3',
    'ujson',
]


if lwp.PY2:
    REQUIREMENTS.append('futures')


setup(
    name='lwp',
    version=lwp.__version__,
    author=lwp.__author__,
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
    # data_files=data_files,
    packages=find_packages(),
    install_requires=REQUIREMENTS
)
