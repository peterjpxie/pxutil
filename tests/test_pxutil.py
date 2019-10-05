"""
Note: 
For pytest to support importing local modules, e.g. power.py, must create a __init__.py file to indicate it is a package.
"""
# Note: relative imports must use this syntax: from <> import <> 
# from ..pxutil import bash, grep, trim_docstring
import pxutil as px
# from pxutil import bash, grep, trim_docstring

def test_bash():
    result = px.bash('ls test_pxutil.py')
    print(result)
    assert result.stdout == 'test_pxutil.py'

def test_grep():
    pass
    
def test_trim_docstring():
    pass    