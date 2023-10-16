# pxutil

[![build-test-publish](https://github.com/peterjpxie/pxutil/actions/workflows/build_test_publish.yml/badge.svg)](https://github.com/peterjpxie/pxutil/actions)
[![black-code-style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Some handy Python utilities

A sample to learn Python packaging

## Install from source

```
python setup.py install
or 
pip install .
```

## Build distributions ( Replaced with Actions / cibuildwheel for multiple python versions and platforms)

```
# build for current python version
rm -rf dist/* && python setup.py sdist bdist_wheel
```

## Build and Test - cibuildwheel locally for current platform

```
pip install cibuildwheel
# build with docker
cibuildwheel --platform linux . 
# cibuildwheel config in pyproject.toml
```

## Publish to pypi ( Replaced with Actions / cibuildwheel for multiple python versions and platforms)

```
twine upload dist/*
```

## Github Actions

The github action workflow has been configured to run build, test and publish to pypi with cibuildwheel which builds cython extension for multiple python versions and platforms.

The workflow is configured to run manually, not to waste resources on each commit, or automatically when a release is created.

The publish job is executed only when a release is created.

## Usage - Functions
```
import pxutil as px

px.bash('ls')

px.bashx('ls')

px.grep('ab','abc\ndef')

px.normal_path('~/project/src/../README.rst')

px.trim_docstring('''
    ab
        cd
    ef
    '''
    )

@px.exit_on_exception
def to_int(any):
    if isinstance(dict):
        return Exception('dict is not supported to convert to int.')
    return int(any)
```

## Usage - CLI
```
px.loop -h  # run a command in loop
px.chat -h  # chat cli based on chatGPT
px.runc -h  # compile and run single c file with gcc
```

## Test

```
git clone https://github.com/peterjpxie/pxutil.git
cd pxutil
pip3 install -r tests/requirements.txt

pytest # current python version

or 

tox # multiple python versions

or

cibuildwheel --platform linux . # multiple python versions in docker
```

## Places to Update Supported Python Versions
```
setup.py        # pypi description
tox.ini         # tox test
pyproject.toml  # cibuildwheel
```