#!/usr/bin/env python3
"""
pxutil CLI scripts

Refer: https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html
"""

import os

# import pdb
import sys
import textwrap
from time import sleep
import argparse
import shutil

# add pxutil/pxutil.py functions and classes to pxutil/__init__.py so that
# it can be imported as `from pxutil import <func>` both outside and inside pxutil package
from pxutil import bashx, register_signal_ctrl_c, ChatAPI
import pxutil as px

# defaults
Chat_Model_Default = "gpt-4.1-mini"


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
        help="interval in seconds between loops (default: 1.0)",
    )
    parser.add_argument(
        "-n",
        "--nloop",
        type=int,
        default=360000,
        help="number of loops (default: infinite)",
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
        description="ChatGPT cli, type q to exit. Set environment variable OPENAI_API_KEY first."
    )
    parser.add_argument(
        "-m",
        "--model",
        default=Chat_Model_Default,
        help=f"OpenAI chatGPT model, {Chat_Model_Default}(default) etc.",
    )
    parser.add_argument(
        "-q",
        "--quick",
        action="store_true",
        help="Quick mode to get answer, e.g., add 'Short answer pls' to chat.",
    )
    args = parser.parse_args()

    register_signal_ctrl_c()
    chat = ChatAPI(model=args.model.strip())
    while True:
        question = input("> ")
        if question in ("q", "quit"):
            break
        if args.quick:
            question += "\nShort answer pls."
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


def ls_mod_main():
    """px.ls.mod CLI script

    List contents of a module/package: submodules, classes, and functions.
    """
    ## Parse command line arguments.
    parser = argparse.ArgumentParser(
        description="List contents of a module/package: submodules, classes, and functions."
    )
    parser.add_argument(
        "module",
        help="module or package name, e.g., os, os.path, website for website.py (.py is auto stripped if provided)",
    )
    args = parser.parse_args()
    if args.module.endswith(".py"):
        args.module = args.module[:-3]
    px.list_module_contents(args.module)


def onefile_main():
    """px.onefile cli

    combine files in a repo into one for LLM prompt, and respect .gitignore and
    an optional spec file in the same format to specify files to include.

    output sample:

    file: a.py
    ```
    content
    ```

    file: b.js
    ```
    content
    ```
    """
    import pathspec

    ## Parse command line arguments.
    parser = argparse.ArgumentParser(
        description="Combine files in a repo into one for LLM prompt, and respect .gitignore and an optional spec file in the same format to specify files to include. Run it in your repo root folder. Inspired by files-to-prompt."
    )
    parser.add_argument(
        "--tldr",
        action="store_true",
        help="sample usages",
    )
    parser.add_argument(
        "-s",
        "--spec",
        help="spec file in the same format as .gitignore but specify files to include, e.g., .includefiles",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="a.md",
        help="output file, default: a.md",
    )
    args = parser.parse_args()

    ## Usage
    usages = f"""\
    # Combine all files in a repo
    px.onefile

    # With spec to include only certain files
    px.onefile -s .includefiles

    spec example: only *.py except tests/*.py
    ---
    *.py
    !tests/*
    ---
    
    spec example: all files except tests/*
    ---
    /*
    !tests/
    ---
    """
    usages = textwrap.dedent(usages)
    if args.tldr:
        print(usages)
        sys.exit()

    ## get files excluding the ones specified in .gitignore
    ## use 'git ls-files' for best match and recursive .gitignore support
    ls_files = []
    if os.path.isdir(".git"):
        if not shutil.which("git"):
            sys.exit("Oops... git command not found. Please install git first.")
        r = px.bash("git ls-files")
        if r.returncode != 0:
            sys.exit(
                f"Error: git ls-files failed with return code: {r.returncode}, stderr: {r.stderr}"
            )
        ls_files = r.stdout.splitlines()
    else:
        # get all files if not a repo
        for root, dirs, files in os.walk("."):
            # For each file, construct relative path to be same output format as git ls-files
            for file in files:
                ls_files.append(os.path.relpath(os.path.join(root, file), "."))

    ## get files included in spec file, e.g., .includefiles
    include_files = None
    spec_file = args.spec
    if spec_file:
        if not os.path.isfile(spec_file):
            sys.exit(f"Error: spec file {spec_file} does not exit.")
        with open(spec_file, "r") as f:
            spec_text = f.read()
        spec = pathspec.GitIgnoreSpec.from_lines(spec_text.splitlines())
        matches = spec.match_tree(".")
        include_files = list(matches)

    ## get intersection of git_ls_files and include_files
    if include_files:
        files = set(ls_files) & set(include_files)
    else:
        files = ls_files

    # exclude binary files
    files = [f for f in files if px.is_text_file(f)]

    output = px.normal_path(args.output)
    if not os.path.isdir(os.path.dirname(output)):
        sys.exit(f"Error: Parent directory of output {args.output} does not exit.")
    with open(output, "w") as out_f:
        # print list of files
        separator = "```"
        file_list = "\n".join(files)
        # fmt: off
        to_output = (
            f"files:\n"
            f"{separator}\n"
            f"{file_list}\n"
            f"{separator}\n\n"
        )
        # fmt: on
        out_f.write(to_output)

        # print content of files
        for file in files:
            with open(file, "r") as f:
                content = f.read()

            # code block separator
            if "```" in content:
                # 4 ticks to escape
                separator = "````"
            else:
                separator = "```"
            # fmt: off
            to_output = (
                f"file: `{file}`\n"
                f"{separator}\n"
                f"{content}\n"
                f"{separator}\n\n"
            )
            # fmt: on
            out_f.write(to_output)
    print(f"one file is generated at {args.output}")


if __name__ == "__main__":
    # self test
    # # add parent directory of pxutil package to sys.path so that we can import the package from inside.
    # sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    # loop_main()
    chat_main()
