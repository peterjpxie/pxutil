pxutil
========
.. image:: https://travis-ci.com/peterjpxie/pxutil.svg?branch=master
    :target: https://travis-ci.com/peterjpxie/pxutil

Some handy Python utils 

Install from source
=======

python setup.py install

or 

pip install .

Build distributions (source and binary wheel)
=======

python setup.py sdist bdist_wheel

Usage
=======
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
