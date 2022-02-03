#!/bin/bash -x 
# 
# Build package

# cross-platform packaging:
# pip install cibuildwheel

rm -rf build/* dist/* pxutil/*.so pxutil.egg-info
python setup.py build_ext --inplace # This is not required for packaging, but for local pytest
python setup.py sdist bdist_wheel # build wheel including build_ext for current python version and current platform
# cibuildwheel --platform linux # cross platform build --output-dir dist
ls -l dist/* pxutil/*.so
