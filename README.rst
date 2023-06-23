pxutil
======
.. image:: https://github.com/peterjpxie/pxutil/actions/workflows/build_test_publish.yml/badge.svg
    :target: https://github.com/peterjpxie/pxutil/actions  
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

Some handy Python utilities

Install from source
===================
::

    python setup.py install
    or 
    pip install .

Build distributions ( Replaced with Actions / cibuildwheel for multiple python versions and platforms)
======================================================================================================
::

    # build for current python version
    rm -rf dist/* && python setup.py sdist bdist_wheel

Build and Test - cibuildwheel locally for current platform
==========================================================
::

    pip install cibuildwheel
    # containerized build
    cibuildwheel --platform linux . 
    # cibuildwheel config in pyproject.toml


Publish to pypi ( Replaced with Actions / cibuildwheel for multiple python versions and platforms)
==================================================================================================
::

    twine upload dist/*


Github Actions
==============
The github action workflow has been configured to run build, test and publish to pypi with cibuildwheel which builds cython extension for multiple python versions and platforms.

The workflow is configured to run manually, not to waste resources on each commit, or automatically when a release is created.

The publish job is executed only when a release is created.


Usage
=====
::

    import pxutil as px
    from pxutil import exit_on_exception

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

    @exit_on_exception
    def to_int(any):
        if isinstance(dict):
            return Exception('dict is not supported to convert to int.')
        return int(any)

Test
====
::

    pip3 install -U pytest tox pytest-cov 

    git clone https://github.com/peterjpxie/pxutil.git

    cd pxutil

    pytest # current python version

    or 

    tox # multiple python versions

    or

    cibuildwheel --platform linux . # multiple python versions in docker
