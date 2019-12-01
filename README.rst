pxutil
========
.. image:: https://travis-ci.com/peterjpxie/pxutil.svg?branch=master
    :target: https://travis-ci.com/peterjpxie/pxutil

Peter Jiping Xie's personal Python utils 

Build source distribution
=======

python setup.py sdist

Install from source
=======

python setup.py install

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
