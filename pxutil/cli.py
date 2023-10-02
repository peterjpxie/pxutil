#!/usr/bin/env python3
"""
pxutil CLI scripts

Refer: https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html
"""

import os
import sys
import logging
from time import sleep
import argparse

# add .pxutil functions / classes to pxutil/__init__.py so that it can be imported as `from pxutil import <func>` both outside and inside pxutil package
from pxutil import (bashx, register_signal_ctrl_c, ChatAPI)


def loop_main():
    """ px.loop CLI script

    Loop a command with interval and number of loops
    """
    parser = argparse.ArgumentParser(description='Loop a command')
    parser.add_argument('cmd', type=str, help='command to loop, double quote if it contains spaces')
    parser.add_argument('-i', '--interval', type=float, default=1.0, help='interval in seconds between loops')
    parser.add_argument('-n', '--nloop', type=int, default=360000, help='number of loops, infinitely by default')
    args = parser.parse_args()
    
    register_signal_ctrl_c()
    for _ in range(args.nloop):
        bashx(args.cmd)
        sleep(args.interval)


def chat_main():
    """ px.chat CLI script

    chat based on chatGPT API
    """
    parser = argparse.ArgumentParser(description='ChatGPT cli, type q to exit. Set env variable OPENAI_API_KEY first.')
    parser.add_argument('--v4', action='store_true', help='use GPT-4, default is GPT-3.5 turbo')
    args = parser.parse_args()
    
    register_signal_ctrl_c()
    if args.v4:
        model = 'gpt-4'
    else:
        model = 'gpt-3.5-turbo'
    chat = ChatAPI(model=model)
    while True:
        question = input('> ')
        if question in ('q', 'quit'):
            break
        answer = chat.chat(question)
        print(answer)


if __name__ == "__main__":
    # self test
    # # add parent directory of pxutil package to sys.path so that we can import the package from inside.
    # sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
    # loop_main()
    chat_main()