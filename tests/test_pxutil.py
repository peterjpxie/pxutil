"""
Note: 
For pytest to support importing local modules, must create a __init__.py file to indicate it is a package.
"""
# Note: relative imports must use this syntax: from <> import <>
# from ..pxutil import bash, grep, trim_docstring
# Somehow direct import works with magic with pytest, even without tox or install pxutil as a system package.
# Not sure how it works exactly, rename __init__.py and setup.py from parent folder but it still works.
import pxutil as px


def test_bash():
    ret = px.bash("ls")
    # print(ret)
    assert ret.returncode == 0


def test_grep():
    ret = px.grep("de", "abc\ndef")
    # print(ret)
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
    """
    TODO
    """
    pass 
    # import tempfile
    # 
    # # tempfile supports only bytes format
    # with tempfile.TemporaryFile() as f:
    #     f.write(b'Hello world!\Hello you.')
    