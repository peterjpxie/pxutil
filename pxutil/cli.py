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
import shutil

# add .pxutil functions / classes to pxutil/__init__.py so that it can be imported as `from pxutil import <func>` both outside and inside pxutil package
from pxutil import bashx, register_signal_ctrl_c, ChatAPI
import pxutil as px


def loop_main():
    """px.loop CLI script

    Loop a command with interval and number of loops
    """
    parser = argparse.ArgumentParser(description="Loop a command")
    parser.add_argument(
        "cmd", type=str, help="command to loop, double quote if it contains spaces"
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=1.0,
        help="interval in seconds between loops",
    )
    parser.add_argument(
        "-n",
        "--nloop",
        type=int,
        default=360000,
        help="number of loops, infinitely by default",
    )
    args = parser.parse_args()

    register_signal_ctrl_c()
    for _ in range(args.nloop):
        bashx(args.cmd)
        sleep(args.interval)


def chat_main():
    """px.chat CLI script

    chat based on chatGPT API
    """
    parser = argparse.ArgumentParser(
        description="ChatGPT cli, type q to exit. Set env variable OPENAI_API_KEY first."
    )
    parser.add_argument(
        "--v4", action="store_true", help="use GPT-4-turbo, default is GPT-3.5-turbo"
    )
    args = parser.parse_args()

    register_signal_ctrl_c()
    if args.v4:
        model = "gpt-4-turbo"
    else:
        model = "gpt-3.5-turbo"
    chat = ChatAPI(model=model)
    while True:
        question = input("> ")
        if question in ("q", "quit"):
            break
        answer = chat.chat(question)
        print(answer)


def runc_main():
    """px.runc CLI script

    Compile single C file with gcc and execute it.
    """

    ## Parse command line arguments.
    parser = argparse.ArgumentParser(
        description="Compile single C file with gcc and execute it."
    )
    parser.add_argument("file", help="C file to compile and run")
    parser.add_argument(
        "-O",
        "--optimization",
        type=int,
        default=0,
        help="optimization level (0, 1, 2, 3, s, g, fast), default: 0",
    )
    args = parser.parse_args()

    ## Check if gcc is installed.
    if not shutil.which("gcc"):
        print("gcc is not installed. Exiting...")
        sys.exit(1)

    ## main
    cmd = f"gcc -O{args.optimization} {args.file} -o a.out && ./a.out"
    bashx(cmd)


def listmod_main():
    """px.listmod CLI script

    List contents of a module/package: submodules, classes, and functions.
    """
    ## Parse command line arguments.
    parser = argparse.ArgumentParser(
        description="List contents of a module/package: submodules, classes, and functions."
    )
    parser.add_argument("module", help="module or package name, e.g., os, os.path, website for website.py")
    args = parser.parse_args()
    px.list_module_contents(args.module)


if __name__ == "__main__":
    # self test
    # # add parent directory of pxutil package to sys.path so that we can import the package from inside.
    # sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    # loop_main()
    listmod_main()
