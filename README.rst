pxutil
======
.. image:: https://travis-ci.com/peterjpxie/pxutil.svg?branch=master
    :target: https://travis-ci.com/peterjpxie/pxutil

Some handy Python utilities

Install from source
===================

python setup.py install

or 

pip install .

Build distributions (source and binary wheel)
=============================================

rm -rf dist/*

python setup.py sdist bdist_wheel

Publish to pypi
===============

twine upload dist/*

Usage
=====
::

    import pxutil as px

    px.bash('ls')

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
