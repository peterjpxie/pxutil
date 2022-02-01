#!/bin/bash -x 
# 
# Build package

# cross-platform packaging:
# pip install cibuildwheel

rm -rf dist/* pxutil/*.so pxutil.egg-info
python setup.py build_ext --inplace # build cython module
python setup.py sdist bdist_wheel # build wheel
ls -l dist/* pxutil/*.so
