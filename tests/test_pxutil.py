"""
Note: 
For pytest to support importing local modules, must create a __init__.py file to indicate it is a package.
"""
# Note: relative imports must use this syntax: from <> import <>
# from ..pxutil import bash, grep, trim_docstring
# Somehow direct import works with magic with pytest, even without tox or install pxutil as a system package.
# Not sure how it works exactly, rename __init__.py and setup.py from parent folder but it still works.
import platform
import pxutil as px
from pxutil import (
    exit_on_exception,
    normal_path,
    set_work_path,
    prepend_sys_path,
    import_any,
)
import os
import io
import sys
import pytest
import os.path as osp
import json
import time


def test_bash():
    if os.name == "posix":
        ret = px.bash("pwd")
        assert ret.returncode == 0


def test_bashx():
    import os
    import io
    import sys

    if os.name == "posix":
        ## test default
        cmd = "pwd"
        ret = px.bashx(cmd)
        assert ret.returncode == 0

        ## test x=False
        capturedOutput = io.StringIO()  # Create StringIO object
        sys.stdout = capturedOutput  # and redirect stdout.

        ret = px.bashx(cmd, x=False)  # capture stdout of print
        standard_output = capturedOutput.getvalue()

        sys.stdout = sys.__stdout__  # Reset redirect.
        assert ("+ %s" % cmd) not in standard_output
        assert ret.returncode == 0

        ## test x=False by environment variable BASH_CMD_PRINT
        os.environ["BASH_CMD_PRINT"] = "False"
        capturedOutput = io.StringIO()  # Create StringIO object
        sys.stdout = capturedOutput  # and redirect stdout.

        ret = px.bashx(cmd, x=True)  # capture stdout of print
        standard_output = capturedOutput.getvalue()

        sys.stdout = sys.__stdout__  # Reset redirect.
        assert ("+ %s" % cmd) not in standard_output
        assert ret.returncode == 0

        ## test e=True
        # Ref: https://docs.pytest.org/en/6.2.x/assert.html#assertions-about-expected-exceptions
        cmd = "ls not_exit"
        # Capture SystemExit exception raised by sys.exit
        with pytest.raises(SystemExit) as excinfo:
            px.bashx(cmd, e=True)
        assert excinfo.type == SystemExit

        ## test e=True by environment variable BASH_EXIT_ON_ERROR
        os.environ["BASH_EXIT_ON_ERROR"] = "true"
        cmd = "ls not_exit"
        # Capture SystemExit exception raised by sys.exit
        with pytest.raises(SystemExit) as excinfo:
            px.bashx(cmd, e=False)
        assert excinfo.type == SystemExit


def test_grep():
    ret = px.grep("de", "abc\ndef")
    assert ret == ["def"]


def test_trim_docstring():
    ret = px.trim_docstring(
        """
    ab
        cd
    """
    )
    # print(ret)
    assert ret == "ab\n    cd"


def test_replace_in_file():
    import os

    tempfile = "test_replace_in_file.tmp"
    with open(tempfile, mode="w+") as f:
        f.write("Hello world\nHello you.")

    # test 1 file
    px.replace_in_file(tempfile, "Hello", "Hi", backup=None)
    with open(tempfile, mode="r") as f:
        assert f.read() == "Hi world\nHi you."

    # test file list
    px.replace_in_file(
        [
            tempfile,
        ],
        "Hi",
        "Hey",
        backup=None,
    )
    with open(tempfile, mode="r") as f:
        assert f.read() == "Hey world\nHey you."

    os.remove(tempfile)

    # import tempfile
    # # tempfile is removed on close. Need a persistent temp file for this test
    # with tempfile.TemporaryFile(mode='w+') as f:
    #     f.write('Hello world!\nHello you.')
    #     f.seek(0)
    #     print(f.read())


def test_normal_path():
    # test resolution of a relative path to a full path
    # Note: On CI windows runner, it asserts 'C:\\a.txt' == 'c:\\a.txt'.
    #       realpath() returns 'C:\\a.txt' but os.getcwd() returns 'c:\' in lower case.
    current_dir = os.getcwd()
    assert normal_path("a.txt").lower() == os.path.join(current_dir, "a.txt").lower()

    if os.name == "posix":
        # test normalization of a path with up-level references and redundant separators
        assert normal_path("/usr/local//../bin/") == "/usr/bin"

        # test resolution of a symbolic link to the actual path
        # get full real path of current python interpreter
        python_path = os.path.realpath(sys.executable)
        os.symlink(python_path, "tmp_python")
        try:
            assert normal_path("tmp_python", resolve_symlink=True) == python_path
        finally:
            os.remove("tmp_python")

        # test expansion of an environment variable reference to its value
        # Note: On mac, this does not work, '$HOME/mydir' becomes /System/Volumes/Data/home/peter/mydir.
        if platform.system() == "Linux":
            # don't override $HOME as it will impact other tests. Use env variable HOMETEST instead.
            os.environ["HOMETEST"] = "/home/peter"
            assert normal_path("$HOMETEST/mydir") == "/home/peter/mydir"

        # test expansion of a tilde to the user's home directory
        # Note: On mac ~root is /private/var/root
        if platform.system() == "Linux":
            assert normal_path("~root/mydir") == "/root/mydir"
        # NB: On macOS, ~root is /var/root sometimes, but /private/var/root other times.
        elif platform.system() == "Darwin":
            assert normal_path("~root/mydir") in [
                "/private/var/root/mydir",
                "/var/root/mydir",
            ]


def test_set_work_path():
    """test set_work_path"""
    with set_work_path("~") as p:
        assert os.getcwd() == normal_path("~")
        # print(os.getcwd())


def test_prepend_sys_path():
    """test prepend_sys_path"""
    import tempfile

    # test with unique temp dir
    with tempfile.TemporaryDirectory() as temp_dir:
        with prepend_sys_path(temp_dir) as p:
            # print('sys path prepended:', sys.path)
            assert sys.path[0] == normal_path(p)
        # temp_dir should be removed after with block
        assert sys.path[0] != normal_path(p)
        # print('sys path restored:', sys.path)


def test_import_any():
    """test import_any"""
    import tempfile

    # test with unique temp dir
    with tempfile.TemporaryDirectory() as temp_dir:
        # create a temp file
        temp_file = osp.join(temp_dir, "temp_file.py")
        with open(temp_file, "w") as f:
            f.write("a = 1")
        tempfile = import_any(temp_file)
        # cleanup temp_file
        os.remove(temp_file)
        assert tempfile.a == 1


def test_setup_logger():
    from pxutil import setup_logger
    import logging

    ## default logger format, stdout
    capturedOutput = io.StringIO()  # Create StringIO object
    origin_stdout = sys.stdout
    sys.stdout = capturedOutput  # and redirect stdout.

    logger1 = setup_logger(logging.INFO)
    logger1.info("info log")

    standard_output = capturedOutput.getvalue()
    sys.stdout = origin_stdout  # Reset redirect.

    assert "info log" in standard_output, "The log does not contain 'info log'"

    ## default logger format, file
    log_file = "a.log"
    logger2 = setup_logger(logging.INFO, log_file, name="file_logger", mode="w")
    logger2.info("info log")

    with open(log_file) as f:
        content = f.read()
        assert "info log" in content, "The log does not contain 'info log'"

    # cleanup
    for handler in logger2.handlers:
        handler.close()
        logger2.removeHandler(handler)
    # avoid file not closed quick enough
    time.sleep(0.01)
    os.remove(log_file)

    ## simple time only format, stdout
    log_file = "a.log"
    logger3 = setup_logger(
        logging.INFO,
        log_file,
        name="time_only",
        formatter_simple_time_only=True,
        mode="w",
    )
    logger3.info("good for API logging")

    with open(log_file) as f:
        content = f.read()
        assert "INFO" not in content, "The log does not contain log level 'INFO'"

    # cleanup
    for handler in logger3.handlers:
        handler.close()
        logger3.removeHandler(handler)
    # avoid file not closed quick enough
    time.sleep(0.01)
    os.remove(log_file)


def test_read_env_file():
    from pxutil import read_env_file

    ## Test with a valid .env file
    file_path = "test_valid.env"
    with open(file_path, "w") as f:
        f.write("KEY1=value1\n")
        f.write("KEY2=value2\n")
        f.write("# This is a comment\n")
        f.write("\n")  # Empty line

    expected_output = {"KEY1": "value1", "KEY2": "value2"}
    result = read_env_file(file_path)
    assert result == expected_output

    # Clean up
    os.remove(file_path)

    ## Test with a non-existent file
    file_path = "non_existent.env"
    result = read_env_file(file_path)
    assert isinstance(result, Exception)
    assert str(result) == f"The file {file_path} does not exist."
