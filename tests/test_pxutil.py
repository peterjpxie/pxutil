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
import sys
import pytest
import os.path as osp
import json


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


def test_request():
    """test request"""
    from pxutil import request
    import requests

    # Test GET request
    get_url = "https://httpbin.org/get"
    response = request("GET", get_url)
    assert isinstance(response, dict)
    assert response["url"] == get_url

    # Test POST request with JSON data and headers
    post_url = "https://httpbin.org/post"
    json_data = {"key": "value"}
    headers = {"My-Header": "value"}
    response = request("POST", post_url, data=json.dumps(json_data), headers=headers)
    assert isinstance(response, dict)
    assert response["json"] == json_data
    assert response["headers"]["My-Header"] == "value"

    ## Test session with cookies
    # Create a Session object to persist cookies
    session = requests.Session()

    set_cookie_url = "https://httpbin.org/cookies/set/sessioncookie/123456789"
    get_cookies_url = "https://httpbin.org/cookies"

    # Set a cookie
    # This url will redirect to get_cookies_url while setting the cookies, we don't need that so set allow_redirects=False.
    response = request("GET", set_cookie_url, session=session, allow_redirects=False)
    assert isinstance(response, Exception) is False

    # Make another request to check cookies persistence
    # get_cookies_url will return cookies in the request as json body response
    response = request("GET", get_cookies_url, session=session)
    assert response == {"cookies": {"sessioncookie": "123456789"}}


def test_post():
    """test post, a shorthand of request"""
    from pxutil import post

    # Test POST request with JSON data and headers
    post_url = "https://httpbin.org/post"
    json_data = {"key": "value"}
    headers = {"My-Header": "value"}
    response = post(post_url, data=json.dumps(json_data), headers=headers)
    assert isinstance(response, dict)
    assert response["headers"]["My-Header"] == "value"


def test_setup_logger():
    import logging
    # default logger format, stdout
    logger1 = setup_logger(logging.INFO)
    logger1.info()
    # default logger format, file

    # simple time only format, stdout 


def setup_logger(
    level=logging.INFO,
    log_file=None,
    name=__name__,
    formatter=None,
    formatter_simple_time_only=False,
    mode="a",
    rotate=True,
    maxBytes=1024000,
    backup_count=5,
):