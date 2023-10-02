#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup, Extension
from Cython.Build import cythonize

_version = "0.0.20"

with open("README.md") as readme:
    long_description = readme.read()
    # print(long_description)

# extensions = [
#     Extension("*", ["*/*.pyx"],
#         # include_dirs=[...],
#         # libraries=[...],
#         # library_dirs=[...]
#         ),
# ]

setup(
    name="pxutil",
    version=_version,
    description="Some handy Python tools",
    long_description=long_description,
    long_description_content_type='text/markdown', # default is text/x-rst # "text/markdown"
    author="Peter Jiping Xie",
    author_email="peter.jp.xie@gmail.com",
    url="https://github.com/peterjpxie/pxutil.git",
    license="MIT",
    packages=find_packages(),
    python_requires='>=3.7', # temp: support 3.7 for now though officially built for 3.8+
    install_requires=[
        'requests>=2.1.0',
        'cython>=3.0.0',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
    ],
    # build cython modules
    ext_modules=cythonize("*/*_cy.py"), # pure python with cython type annotation
    # ext_modules=cythonize("*/*.pyx"), # language_level="3"
    # ext_modules=cythonize(extensions),
    zip_safe=False,
    # shared lib from Cython - No need! setup.py build and include them in the wheel automatically.
    # package_data={'': ['pxutil/*.so', 'pxutil/*.dll', 'pxutil/*.pyd']},
    # cli
    entry_points = {
        'console_scripts': ['px.loop=pxutil.cli:loop_main',
                            'px.chat=pxutil.cli:chat_main',
                            'chat=pxutil.cli:chat_main'],
    },
)
