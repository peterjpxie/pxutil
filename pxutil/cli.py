#!/usr/bin/env python3
"""
pxutil CLI scripts

Refer: https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html
"""

import os
import sys
import logging
from time import sleep
from pxutil import (bashx, register_signal_ctrl_c)


def loop_main():
    """ px.loop CLI script

    Loop a command with interval and number of loops
    """
    import argparse
    parser = argparse.ArgumentParser(description='Loop a command')
    parser.add_argument('cmd', type=str, help='command to loop, double quote if it contains spaces')
    parser.add_argument('-i', '--interval', type=float, default=1.0, help='interval in seconds between loops')
    parser.add_argument('-n', '--nloop', type=int, default=360000, help='number of loops, infinitely by default')
    args = parser.parse_args()
    
    register_signal_ctrl_c()
    for _ in range(args.nloop):
        bashx(args.cmd)
        sleep(args.interval)
    
if __name__ == "__main__":
    # self test
    loop_main()