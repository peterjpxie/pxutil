#!/usr/bin/env python3
"""
Sample __main__.py to be executed as python -m <pxutil>

Ref: 
https://docs.python.org/3/library/__main__.html
pip.__main__.py
"""
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This is a sample __main__.py to execute as `python -m pxutil.`')
    args = parser.parse_args()
    print('This is a sample __main__.py to execute as `python -m pxutil.`')