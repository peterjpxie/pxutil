#!/usr/bin/env python
# # coding: utf-8
from setuptools import find_packages, setup

with open('README.rst') as readme:
    long_description = readme.read()

setup(
    name='pxutil',
    description='Some personal python utils',
    version='0.1',
    long_description=long_description,
    author='Peter Jiping Xie',
    author_email='peter.jp.xie@gmail.com',
    url='https://github.com/peterjpxie/pxutil.git',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: MIT',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
