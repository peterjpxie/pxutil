"""
Some handy utilities from Peter Jiping Xie  
"""
# __all__ = ['bash','trim_docstring','grep']

import sys
import logging
import re

if sys.version_info < (3, 5):
    raise Exception("Require python 3.5 or above.")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s ln-%(lineno)-3d %(levelname)7s: %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S",
)
log = logging.getLogger("pxutil")


def bash(cmd):
    """    
    subprocess.run with intuitive options to execute system commands just like shell bash command.
    
    Inspired by https://pypi.org/project/bash/.
    
    cmd: string or list 
    return: CompletedProcess object in text (decode as utf-8), with attributes stdout, stderr and returncode.
    
    Usage example: 
    ret = bash('ls')
    print(ret.stdout, ret.stderr, ret.returncode)
    
    Warning of using shell=True: https://docs.python.org/2/library/subprocess.html#frequently-used-arguments
    """
    from subprocess import run, PIPE  # , Popen, CompletedProcess
    import sys

    if sys.version_info >= (
        3,
        7,
    ):  # version_info is actually a tuple, so compare with a tuple
        return run(cmd, shell=True, capture_output=True, text=True)

    elif sys.version_info >= (3, 6):
        # Not supported parameters: capture_output=True, text = True
        return run(cmd, shell=True, stdout=PIPE, stderr=PIPE, encoding="utf-8")

    elif sys.version_info >= (3, 5):
        # Not supported parameters: encoding='utf-8'
        r = run(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        r.stdout = r.stdout.decode("utf-8")
        r.stderr = r.stderr.decode("utf-8")
        return r
    else:
        raise Exception("Require python 3.5 or above.")
        # Alternately can call Popen directly, but it will return stderr, stdout as bytes and need to decode first. Don't bother, just upgrade Python version.
        """ Example
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        code = p.returncode
        """


def trim_docstring(docstring):
    """
    Trim leading indents, leading and trailing blank lines from multiple liner using triple quote like docstring.
    
    Reference: https://www.python.org/dev/peps/pep-0257/#handling-docstring-indentation
    
    Argument: multiple liner string, typically using triple quote.
    Return: trimmed multiple line string 
    
    Note: textwrap.dedent(docstring) does the same job, but not removing leading blank lines.
    """
    import sys

    if not docstring:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = (
        sys.maxsize
    )  # sys.maxint in Python 2 is replaced with sys.maxsize in Python 3
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return "\n".join(trimmed)


def grep(pattern, string=None, filename=None):
    """ simulate linux grep command
    
    return lines matching a pattern in a string or a file.
    
    Parameters:
    pattern: regular expression string
    
    Usage examples:
    result = grep('keyword', filename='a.txt' )
    for i in result:
        print(i)
        
    Notes: 
    If the matched list is too big, you can modify it to use yield generator.
    """
    if string == None and filename == None:
        log.error('grep: No string nor filename provided in the arguments.')
        return []
    if string != None:
        extended_pattern = ".*" + pattern + ".*"
        return re.findall(extended_pattern, string)
    if filename != None:
        result = []
        with open(filename) as f:
            extended_pattern = ".*" + pattern + ".*"
            for l in f:
                result += re.findall(extended_pattern, l)
        return result

def replace_in_file(filename, old, new, backup=None):
    """
    Replace in place directly on a file.
    
    Arguments:
        old - old string to replace
        new - new string 
        backup - backup file suffix, e.g. '.bak'. None means no backup
    """
    import fileinput

    with fileinput.FileInput(filename, inplace=True, backup=backup) as file:
        for line in file:
            # yes, this print will write into the file instead to stdout.
            # end = '' so it does not print another blank new line.
            print(line.replace(old, new), end='')   


def test_self():
    mystr = """
    asd 
    dfe 
    """
    print("Before trim:\n" + mystr)
    mystr = trim_docstring(mystr)
    print("After trim:\n" + mystr)


if __name__ == "__main__":
    test_self()
