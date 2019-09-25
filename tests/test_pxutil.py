"""
Note: 
For pytest to support importing local modules, e.g. power.py, must create a __init__.py file to indicate it is a package.
"""
# Note: relative imports must use this syntax: from <> import <> 
from ..pxutil import bash, grep, trim_docstring

def test_bash():
    pass

def test_grep():
    pass
    
def test_trim_docstring():
    pass    