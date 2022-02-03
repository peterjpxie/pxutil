#!/bin/bash -x 
# 
# Build package

# cross-platform packaging:
# pip install cibuildwheel

rm -rf build/* dist/* pxutil/*.so pxutil.egg-info
python setup.py sdist bdist_wheel # build wheel including build_ext
# cibuildwheel --platform linux # cross platform build --output-dir dist
ls -l dist/* 
