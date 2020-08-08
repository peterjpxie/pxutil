#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

with open("README.rst") as readme:
    long_description = readme.read()

setup(
    name="pxutil",
    version="0.0.1",
    description="Some personal python utils",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author="Peter Jiping Xie",
    author_email="peter.jp.xie@gmail.com",
    url="https://github.com/peterjpxie/pxutil.git",
    license="MIT",
    packages=find_packages(),
    python_requires='>=3.5',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Windows",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
    ],
)
