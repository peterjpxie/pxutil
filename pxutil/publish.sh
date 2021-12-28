#!/bin/bash
# 
# Publish package to PyPi
set -x

rm -rf dist/* && \
python setup.py sdist bdist_wheel && \
twine upload dist/*
