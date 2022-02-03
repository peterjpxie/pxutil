#!/bin/bash
# 
# Publish package to PyPi
# Note: This script is obselete as we include cython and need to pulish cross-platform builds 
# through cibuildwheel using Github Actions CI.
set -x

rm -rf dist/* && \
python setup.py sdist bdist_wheel && \
twine upload dist/*
