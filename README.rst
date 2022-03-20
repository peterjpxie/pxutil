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

Build distributions -- Replaced with Actions / cibuildwheel
===========================================================
::

    rm -rf dist/* && python setup.py sdist bdist_wheel

Publish to pypi
===============
::

    twine upload dist/*

Usage
=====
::

    import pxutil as px

    px.bash('ls')

    px.bashx('ls')

    px.grep('ab','abc\ndef')

    px.trim_docstring('''
        ab
            cd
        ef
        '''
        )

Test
====
::

    pip3 install -U pytest tox pytest-cov 

    git clone https://github.com/peterjpxie/pxutil.git

    cd pxutil

    pytest

    or 

    tox
