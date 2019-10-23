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
    result = px.bash('ls')
    # print(result)
    assert result.returncode == 0

def test_grep():
    pass
    
def test_trim_docstring():
    pass    
