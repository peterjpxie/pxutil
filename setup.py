#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

with open("README.rst") as readme:
    long_description = readme.read()
    print(long_description)

setup(
    name="pxutil",
    version="0.0.4",
    description="Some handy Python utilities",
    long_description=long_description,
    # long_description_content_type="text/markdown", # default is rst
    author="Peter Jiping Xie",
    author_email="peter.jp.xie@gmail.com",
    url="https://github.com/peterjpxie/pxutil.git",
    license="MIT",
    packages=find_packages(),
    python_requires='>=3.5',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries",
    ],
)
