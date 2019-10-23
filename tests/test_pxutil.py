"""
Note: 
For pytest to support importing local modules, e.g. power.py, must create a __init__.py file to indicate it is a package.
"""
# Note: relative imports must use this syntax: from <> import <> 
# from ..pxutil import bash, grep, trim_docstring
#from pxutil import pxutil as px
import pxutil as px

def test_bash():
    result = px.bash('ls')
    # print(result)
    assert result.returncode == 0

def test_grep():
    pass
    
def test_trim_docstring():
    pass    
