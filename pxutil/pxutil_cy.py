#!/usr/bin/env python3
"""pure python with cython type annotation

Install:
pip install cython

To run cython:
1. python setup.py build_ext --inplace
This generates .c source file and .so library file.
2. python cython_call.py
Call cython modules in a normal .py file.
 
time python cython_call.py 500000000
sum: 500000000

real    0m0.025s
user    0m0.020s
sys     0m0.000s
"""
import cython


def run_loop(loop: cython.int):
    i: cython.int
    s: cython.int
    s = 0
    for i in range(loop):
        s += 1
    return s


def fib(n: cython.int):
    if n in (1, 2):
        return 1
    return fib(n - 1) + fib(n - 2)
