#!/usr/bin/env python3
"""
Some handy utilities from Peter Jiping Xie
"""
# __all__ = ['bash','trim_docstring','grep']


import copy
import sys
import re
import os
import json
import logging
from logging.handlers import RotatingFileHandler
from os import path
import os.path as osp
from contextlib import contextmanager
import pdb

import requests

### Settings ###
## log level is not used.
# log_level_str = os.getenv(
#     "PX_LOG_LEVEL", "ERROR"
# )  # DEBUG, INFO, WARNING, ERROR, CRITICAL
# LOG_LEVEL = getattr(
#     logging, log_level_str.upper()
# )  # convert to logging level, e.g. logging.DEBUG

LOG_MODULE_NAME_LEN = 8

# root_path is parent folder of this file
root_path = path.dirname(path.abspath(__file__))


def normal_path(path: str, resolve_symlink=False):
    """return a normalized path

    resolve_symlink: resolve symbolic link to the actual path

    calls os.path.x:
    expanduser: ~/a.txt => /home/user/a.txt
    expandvars: '$HOME/mydir' => /home/user/mydir
    normpath: /usr/local//../bin/ => /usr/bin
    realpath: a.txt => /home/user/project/a.txt (full path);  /usr/local/bin/python3 (symlink) => /usr/bin/python3.8
    abspath: a.txt => /home/user/project/a.txt (full path); /usr/local/bin/python3 (symlink) => /usr/local/bin/python3;
            /usr/local//../bin/ => /usr/bin

    Note: abspath does half realpath + normpath.
    """
    from os.path import expanduser, expandvars, normpath, realpath, abspath

    if resolve_symlink:
        return realpath(normpath(expandvars(expanduser(path))))
    else:
        return abspath(expandvars(expanduser(path)))


class CustomFormatter(logging.Formatter):
    """Custom formatter to truncate module name to N characters."""

    def format(self, record):
        record.module = record.module[:LOG_MODULE_NAME_LEN]
        # Now format the record as usual
        return super().format(record)


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
    """Function to setup as many loggers as you want.

    level:          logging level
    log_file:       path to the log file (path will be auto normalized) or None for console logging
    name:           logger name   NB: To create multiple log files, must use different logger name.
    formatter:      logging.Formatter object, if None, consider formatter_simple_time_only if true or use default_formatter below.
    formatter_simple_time_only:  Boolean, if true and formatter is None, use this format: logging.Formatter("%(asctime)s: %(message)s").
    mode:           file open mode if rotate is False, 'w' for write, 'a' for append (default)
    rotate:         whether to rotate log file
    maxBytes:       maxBytes for rotating file handler
    backup_count:   backup_count for rotating file handler

    return: logger object
    """
    logger = logging.getLogger(name)
    # Check if logger is already configured with the name.
    # This is avoid duplicate log entries when this function is called multiple times with the same log name.
    # Note:
    #   Normally logger.hasHandlers() is False if it is called the first time.
    #   But it could True and logger.handlers == [], if root logger `logging.getLogger()` is called once somewhere else,
    #   e.g., when you run pytest to test this function, pytest seems to call logging.getLogger() first.
    #   hasHandlers() check its parent's handlers as well.
    #   You can test parent relationship w/ code below:
    #   # Creating loggers
    #   root_logger = logging.getLogger()
    #   child_logger = logging.getLogger('module.submodule')
    #   # Check and print the parent of the child_logger
    #   print(f"Logger: {child_logger.name}, Parent: {child_logger.parent.name if child_logger.parent else 'No Parent'}")
    #   # It will output:
    #   # Logger: module.submodule, Parent: root
    if not logger.hasHandlers() or logger.handlers == []:
        if formatter is None:
            # %(levelname)7s to align 7 bytes to right, %(levelname)-7s to left.
            default_formatter = CustomFormatter(
                f"[%(asctime)s][%(levelname)7s][%(module){LOG_MODULE_NAME_LEN}s][%(lineno)4d]: %(message)s",
            )
            if formatter_simple_time_only:
                formatter = logging.Formatter("%(asctime)s: %(message)s")
            else:
                formatter = default_formatter

        # use stream handler for console logging if log_file is None
        if log_file is None:
            # by default steam is stderr. Use stdout to easy redirect in cli
            handler = logging.StreamHandler(stream=sys.stdout)
        else:
            # normalize log_file path
            log_file = normal_path(log_file)

            # create log directory if not exist
            os.makedirs(path.dirname(log_file), exist_ok=True)
            if rotate:
                handler = RotatingFileHandler(
                    log_file, maxBytes=maxBytes, backupCount=backup_count
                )
            else:
                handler = logging.FileHandler(log_file, mode=mode)

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
        # Prevents log messages from being duplicated to the root logger
        logger.propagate = False

    return logger


def pretty_json(json_str):
    """return pretty formatted json string if possible, otherwise return the original

    json_str: The input could be anything, e.g., bytes, and it just returns the original if it is not a valid json string.
    """
    import json

    try:
        json_dict = json.loads(json_str)
        return json.dumps(json_dict, indent=4)
    # ValueError includes: UnicodeDecodeError (e.g. json_str is image binary), json.decoder.JSONDecodeError etc.
    # TypeError includes: dict, int etc.
    except (ValueError, TypeError):
        return json_str


def pretty_print_request_json(request, logger):
    """pretty print request in json format if possible, otherwise print in text or bytes
    Note it may differ from the actual request as it is pretty formatted.

    Params
    ------
    request:    requests' request object
    logger:     logging instance
    """
    # pretty json if possible
    req_body = pretty_json(request.body)

    # decode bytes to string if possible
    # otherwise, replace form raw data (e.g. image) with string '<binary raw data>', then decode to string
    if isinstance(req_body, bytes):
        try:
            req_body = req_body.decode("utf-8")
        except UnicodeDecodeError:
            # replace form raw data with string '<binary raw data>'
            if "multipart/form-data" in request.headers.get("Content-Type"):
                req_body = re.sub(
                    b"(\r\n\r\n)(.*?)(\r\n--)",
                    rb"\1<binary raw data>\3",
                    req_body,
                    flags=re.DOTALL,
                )
                req_body = req_body.decode("utf-8")
            # else unchanged as bytes
            # print(req_body)

    logger.debug(
        "{}\n{}\n\n{}\n\n{}\n".format(
            "-----------Request----------->",
            request.method + " " + request.url,
            "\n".join(f"{k}: {v}" for k, v in request.headers.items()),
            req_body,
        )
    )


def pretty_print_response_json(response, logger):
    """pretty print response in json format
    If failing to parse body in json format, print in text.

    Params
    ------
    response:   requests' response object
    logger:     logging instance
    """
    try:
        resp_data = response.json()
        resp_body = json.dumps(resp_data, indent=4)
    # if .json() fails, ValueError is raised, take text format
    except ValueError:
        resp_body = response.text

    logger.debug(
        "{}\n{}\n\n{}\n\n{}\n".format(
            "<-----------Response-----------",
            "Status code:" + str(response.status_code),
            "\n".join(f"{k}: {v}" for k, v in response.headers.items()),
            resp_body,
        )
    )


def post(
    url,
    *,
    data=None,
    headers={},
    files=None,
    verify=True,
    amend_headers=True,
    content_type=None,
    session=None,
    logger=None,
    **kwargs,
):
    """shorthand for request('POST', ...)"""
    return request(
        "POST",
        url,
        data=data,
        headers=headers,
        files=files,
        verify=verify,
        amend_headers=amend_headers,
        content_type=content_type,
        session=session,
        logger=logger,
        **kwargs,
    )


def request(
    method: str,
    url: str,
    *,  # keyword only argument after this
    data=None,  # NA for GET
    headers={},
    files=None,
    auth=None,  # NA for POST
    verify=True,  # default to True to avoid the annoying warning
    amend_headers=True,  # NA for GET
    content_type=None,
    session=None,
    logger=None,
    **kwargs,
):
    """
    Common request function with below features, which can be used for any request methods such as 'POST', GET, OPTIONS, HEAD, POST, PUT, PATCH, or DELETE:
        - append common headers (when amend_headers=True)
        - print request and response in API log file
        - Take care of request exception and error response codes (>=400) and return None, so you only need to care normal json response.
        - arguments are the same as requests.request, except amend_headers.

    Arguments
    ---------
    method:         Same as requests.request
    url:            Same as requests.request
    data:           Same as requests.request
    headers:        Same as requests.request
    files:          Same as requests.request
    auth:           Same as requests.request
    verify:         Same as requests.request. False - Disable SSL certificate verification, set to False to test dev server with self-signed certificate.
    amend_headers:  boolean, Append common headers, e.g. set Content-Type to "application/json" if body is json
    content_type:   str, set header Content-Type if provided
    session:        requests.Session() instance, send requests in the provided session if set, and will maintain session cookies.
    logger:         logging instance, e.g., logging.getLogger(), to pretty log API request and response in INFO level (please set proper level in the logger).
                    Default to None, no logging.
    kwargs:         Other arguments requests.request takes.

    Return: response decoded as dict if possible,
            or decoded text if not json,
            or original bytes if decoding fails (not likely),
            or '' if response has no body,
            or Exception if any error or response code >=400.
    """
    # append common headers
    # deep copy headers to avoid using the same headers object (default {}) in different requests
    headers_new = copy.deepcopy(headers)
    # set content type to json if not set
    if content_type is not None:
        headers_new["Content-Type"] = content_type
    # check if body is json, then set content type to json
    elif amend_headers is True:
        if data:
            try:
                json.loads(data)
            except (json.JSONDecodeError, TypeError):
                pass
            else:
                headers_new["Content-Type"] = "application/json"

    # send request
    try:
        if session:
            assert isinstance(
                session, requests.Session
            ), "Provided session is not requests.Session() instance"
        else:
            # create a new session
            session = requests.Session()
        resp = session.request(
            method,
            url,
            data=data,
            headers=headers_new,
            files=files,
            auth=auth,
            verify=verify,
            **kwargs,
        )
    except Exception as ex:
        return Exception("request() failed with exception: %s" % str(ex))

    if logger:
        # pretty request and response into API log file
        pretty_print_request_json(resp.request, logger)
        pretty_print_response_json(resp, logger)

    if resp.status_code >= 400:
        error = f"API call to {url} failed with response code {resp.status_code}."
        if resp.text and len(resp.text)>0:
            error = error + f'body:\n{pretty_json(resp.text)}'
        return Exception(error)

    if resp.content:
        # return json if possible
        try:
            return resp.json()
        except requests.exceptions.JSONDecodeError:
            try:
                # It returns string 'A\x11\x12B' for b'\x41\x11\x12\x42' - ascii binary data with unprintable characters (\x11\x12)
                #   NB: print('A\x11\x12B') prints 'AB' in terminal as \x11\x12 are unprintable characters, but will write A^Q^RB to file.
                # It returns unreadable string '��' for b'\xf1\xf2' - non-decodable (>127) utf8 binary data
                return resp.text
            except Exception:
                # most likely won't reach here
                return resp.content
    else:  # no content in response body, i.e. content = b''.
        return ""


def bash(cmd: str, encoding=None):
    """
    subprocess.run with intuitive options to execute system commands just like shell bash command.

    Inspired by https://pypi.org/project/bash/.

    cmd: command in a string, e.g. 'ls -l'
    encoding: encoding to decode output, e.g. 'utf-8'. Auto detected if None.
    return: CompletedProcess object in text (decode as locale encoding), with attributes stdout, stderr and returncode.

    Usage example:
    ret = bash('ls')
    print(ret.stdout, ret.stderr, ret.returncode)

    Warning of using shell=True: https://docs.python.org/3/library/subprocess.html#security-considerations
    """
    from subprocess import run, PIPE  # Popen, CompletedProcess
    import sys
    import locale

    if sys.version_info >= (3, 7):
        return run(cmd, shell=True, capture_output=True, text=True, encoding=encoding)

    elif sys.version_info >= (3, 5):
        if encoding is None:
            # get system default locale encoding
            encoding = locale.getdefaultlocale()[1]
        # print('encoding: %s' % encoding)
        r = run(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        r.stdout = r.stdout.decode(encoding)
        r.stderr = r.stderr.decode(encoding)
        return r
    else:
        raise Exception("Require python 3.5 or above.")


def bashx(cmd, x=True, e=False):
    """
    run system cmd like bash -x

    Print the cmd with + prefix before executing
    Don't capture the output or error

    Arguments
    ---------
    cmd: string - command to run
    x:  When True, print the command with prefix + like shell 'bash -x' before running it
    e:  When True, exit the python program when returncode is not 0, like shell 'bash -e'.

    return
    ------
    CompletedProcess object with only returncode.

    Shell environment variables
    ---------------------------
    You can set the following environment variables which have the same effect of but overwrite argument options.
    BASH_CMD_PRINT=True     same as x=True
    BASH_EXIT_ON_ERROR=True same as e=True

    Usage example:
    ret = shx('ls')
    print(ret.returncode)

    Warning of using shell=True: https://docs.python.org/3/library/subprocess.html#security-considerations
    """
    from subprocess import run  # CompletedProcess
    import sys
    import os

    if sys.version_info >= (
        3,
        5,
    ):  # version_info is actually a tuple, so compare with a tuple
        x_env = os.getenv("BASH_CMD_PRINT", None)
        # BASH_CMD_PRINT overwrites x argument
        if x_env is not None:
            if x_env.lower() == "true":
                x = True
            elif x_env.lower() == "false":
                x = False

        e_env = os.getenv("BASH_EXIT_ON_ERROR", None)
        # BASH_EXIT_ON_ERROR overwrites x argument
        if e_env is not None:
            if e_env.lower() == "true":
                e = True
            elif e_env.lower() == "false":
                e = False

        if x:
            print("+ %s" % cmd)

        ret = run(cmd, shell=True)

        if e and ret.returncode != 0:
            print(
                "[Error] Command returns error code %s. Exiting the program..."
                % ret.returncode
            )
            sys.exit(1)
        else:
            return ret
    else:
        raise Exception("Require python 3.5 or above.")


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
    """simulate linux grep command

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
        print("grep: No string nor filename provided in the arguments.")
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


def replace_in_file(files, old, new, backup=""):
    """
    Replace in place directly on a file.

    Arguments:
    files - single or list of files, e.g. 'a.txt' or ['a.txt',]
    old - old string to replace
    new - new string
    backup - backup file suffix, e.g. '.bak'. None means no backup
    """
    import fileinput

    with fileinput.FileInput(files, inplace=True, backup=backup) as file:
        for line in file:
            # yes, this print will write into the file instead to stdout.
            # end = '' so it does not print another blank new line.
            print(line.replace(old, new), end="")


def time2seconds(time):
    """delta time string to number of seconds

    time: e.g. '2d' for 2 days, supported units: d-day, h-hour, m-minute, s-second
    return: integer number of seconds

    Note: Month and year duration varies. Not worth doing for the sake of simplicity.
    """
    assert (
        len(re.findall(r"^\d+[s|m|h|d]$", str(time))) == 1
    ), "Invalid time string format."
    tmap = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}
    unit = time[-1]
    value = int(time[:-1])
    return value * tmap[unit]


def purge(dir, age="0s", filename_filter="*"):
    """Purge files and subfolders older than certain age

    Params
    ------
    dir:   directory to purge files and subfolders
    age:    e.g. '2h', support d-day, h-hour, m-minute, s-second
    filename_filter:  glob format, e.g. debug.log*

    Usage examples:
    purge('/root/tmp/', '24h', 'debug.log*')

    Note: It retains the parent folder dir. Use shutil.rmtree if you want to remove the folder as well.
    """
    import os
    import time
    from glob import glob
    import shutil

    if not os.path.isdir(dir):
        print("%s is not a valid directory." % dir)
        return 1

    now = time.time()
    fullpath = os.path.join(dir, filename_filter)

    for f in glob(fullpath):
        # use ctime instead of mtime. e.g. youtube-dl downloads a old video from youtube, mtime is retained, but ctime is when it is downloaded.
        if os.stat(f).st_ctime <= now - time2seconds(age):
            # os.remove(f)
            if os.path.isfile(f) or os.path.islink(f):
                try:
                    os.remove(f)
                except OSError as e:
                    print("Failed to remove %s. Reason: %s" % (f, e))
            elif os.path.isdir(f):
                shutil.rmtree(f, ignore_errors=True)


def exit_on_exception(func):
    """Decorator to exit if func returns an exception(error)"""

    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
        if isinstance(ret, Exception):
            print(
                f"[Error] Program exits because {func.__name__}() failed with error:\n{ret}"
            )
            sys.exit(1)
        return ret

    return wrapper


def is_running_foreground():
    """Check if current script is running in foreground

    Examples:
    python a.py : True
    python a.py & : False
    python a.py > a.log : True
    python a.py | tee a.log : True
    nohup python a.py & : False
    nohup python a.py : False (* special case, this is considered as background as input is ignored and output is redirected. - to reconsider as it is running in foreground.)

    ref: https://stackoverflow.com/questions/24861351/how-to-detect-if-python-script-is-being-run-as-a-background-process
    """
    try:
        # e.g.: python a.py
        if os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno()):
            return True
        else:
            # when running as: python script.py &
            return False
    # e.g.: nohup python script.py &
    # or : `python script.py > a.log` or `python script.py | tee a.log`
    except OSError:
        # Consider foreground if running with pipe redirection and stdin is on the terminal.
        # isatty(0) checks if stdin(0) is connected to the terminal
        # if os.isatty(0):
        # e.g. python script.py > a.log
        if sys.stdin.isatty():
            return True
        # nohup python script.py &
        else:
            return False


def register_signal_ctrl_c():
    """Register signal handler for ctrl+c"""
    import signal

    def signal_handler(sig, frame):
        print(" You pressed Ctrl+C! Exiting...")
        sys.exit(1)

    # if is_running_foreground(): - no need. SIGINT won't be captured if running in background.
    signal.signal(signal.SIGINT, signal_handler)


@contextmanager
def set_work_path(path):
    """With statement to set the cwd within the context

    Params
    ------
    path: The path string to the cwd. Note this path will be automatically normalized by normal_path().

    Yield: cwd path string

    Example:
    with set_work_path('./tmp') as p:
        os.system('ls')
    """
    origin = os.getcwd()
    try:
        path = normal_path(path)
        os.chdir(path)
        yield path
    finally:
        os.chdir(origin)


@contextmanager
def prepend_sys_path(path):
    """With statement to prepend path to sys.path within the context

    path: The path string to prepend. Note this path will be automatically normalized by normal_path().
    Yield: normalized path string

    Example:
    with prepend_sys_path('./tmp') as p:
        import this_module
    """
    sys_path_changed = False
    try:
        path = normal_path(path)
        if path not in sys.path:
            sys.path.insert(0, path)
            sys_path_changed = True
        yield path
    finally:
        if sys_path_changed:
            sys.path.remove(path)


def import_any(path: str):
    """import any module from a path regardless of sys.path

    It will automatically prepend the parent directory of path to sys.path if not already in, and remove it after import.

    Params
    ------
    path: path to a module, e.g., ./config/a.py, /home/user/config/a.py
    return: imported module

    Usage:
        a = import_any('./config/a.py')
        a.func()
    """
    from importlib import import_module

    path = normal_path(path)
    if not osp.isfile(path):
        raise FileNotFoundError(f"Failed to import as file {path} does not exist.")

    with prepend_sys_path(osp.dirname(path)):
        module_name = osp.splitext(osp.basename(path))[0]
        module = import_module(module_name)
        return module


class ChatAPI:
    """chat based on chatGPT API

    Sample REST API
    ---------------
    2023-03-04 04:20:10: -----------Request----------->
    POST https://api.openai.com/v1/chat/completions

    Content-Type: application/json
    Authorization: Bearer <OPENAI_API_KEY>
    Content-Length: 269

    {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Who won the world series in 2020?"
            }
        ]
    }

    2023-03-04 04:20:10: <-----------Response-----------
    Status code:200

    Content-Type: application/json
    Content-Length: 339

    {
        "id": "chatcmpl-6qEbRaIelLcwo12GOssLlPRosGys7",
        "object": "chat.completion",
        "created": 1677907209,
        "model": "gpt-3.5-turbo-0301",
        "usage": {
            "prompt_tokens": 28,
            "completion_tokens": 15,
            "total_tokens": 43
        },
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "The Los Angeles Dodgers won the World Series in 2020."
                },
                "finish_reason": "stop",
                "index": 0
            }
        ]
    }
    """

    def __init__(
        self,
        url="https://api.openai.com/v1/chat/completions",
        token=os.environ.get(
            "OPENAI_API_KEY", None
        ),  # default to environment variable OPENAI_API_KEY
        system_msg=None,
        model="gpt-4o",
        remember_chat_history=True,
        max_chat_history=2,  # each chat has 2 messages, a question and an answer
    ):
        self.url = url
        assert token, "OpenAI token cannot be None."
        self.token = token
        self.model = model
        self.system_msg = system_msg
        self.remember_chat_history = remember_chat_history
        self.chat_history = []  # list of past chat messages
        self.max_chat_history = max_chat_history

    def chat(self, question: str):
        """Ask a question and get an answer

        return: answer str or Exception
        """
        messages = []
        # add system message
        if self.system_msg:
            messages.append({"role": "system", "content": self.system_msg})
        # add chat history
        if self.remember_chat_history and len(self.chat_history) > 0:
            # take only max_chat_history. NB: each chat has 2 messages.
            chat_history = self.chat_history[-self.max_chat_history * 2 :]
            messages.extend(chat_history)
        # add current question
        messages.append({"role": "user", "content": question})
        payload = {
            "model": self.model,  # "gpt-3.5-turbo",
            "messages": messages,
        }
        # messages sample:
        #    "messages": [
        #        {"role": "system", "content": "You are a helpful assistant."}, # appreciation may help get a better answer
        #        {"role": "user", "content": "Who won the world series in 2020?"},
        #        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        #        {"role": "user", "content": "Where was it played?"},
        #    ]

        headers = {"Authorization": "Bearer %s" % self.token}
        # no indent for payload to save possible tokens
        resp = post(self.url, headers=headers, data=json.dumps(payload))
        if isinstance(resp, Exception):
            return Exception("Chat API request failed with error: %s." % resp)

        if len(resp["choices"]) >= 1:  # type: ignore
            for choice in resp["choices"]:  # type: ignore
                if choice["index"] == 0 and choice["finish_reason"] in ("stop", None):  # type: ignore
                    answer = choice["message"]["content"]  # type: ignore
                    answer = answer.strip("\n").strip()
                    # record chat history
                    if self.remember_chat_history:
                        self.chat_history.append({"role": "user", "content": question})
                        self.chat_history.append(choice["message"])  # type: ignore
                    return answer

        return Exception(
            "Chat API request failed with no answer choices."
        )  # default if no answer is found in the response


def list_module_contents(module_name: str):
    """List contents of a module/package: submodules, classes, and functions."""
    import inspect, pkgutil, importlib

    # add CWD to sys.path if not already in, to support modules in CWD when run anywhere as CLI script px.ls.mod
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
    try:
        # Import the module based on the provided name
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        print(f"Module '{module_name}' not found with error: {e}.")
        return

    print(f"Listing contents of module: {module_name}")

    # Try to list submodules if it is a package
    print("\nSubmodules:")
    if hasattr(module, "__path__"):  # Check if module is a package
        for _, name, ispkg in pkgutil.iter_modules(module.__path__):
            print(f"- {name} (Package: {ispkg})")
    else:
        print(f"No submodules in {module_name}")

    # List classes defined in the module (excluding imported classes)
    print("\nClasses:")
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module_name:
            print(f"- {name}")

    # List functions defined in the module (excluding imported functions)
    print("\nFunctions:")
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        if obj.__module__ == module_name:
            print(f"- {name}")


def read_env_file(file_path: str):
    """
    Reads a .env file (ini file w/o section header) and returns a dictionary of environment variables.

    file_path: Path to the .env file.
    return: Dictionary with key-value pairs of environment variables or Exception if any. 
        Note it is all string values. And return empty dict {} if no environment variables set.
    """
    env_vars = {}
    
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Strip whitespace and ignore comments or empty lines
                stripped_line = line.strip()
                if stripped_line == '' or stripped_line.startswith('#'):
                    continue
                
                # Split the line into key and value parts
                key_value_pair = stripped_line.split('=', 1)
                if len(key_value_pair) != 2:
                    continue  # Invalid line without '=' character

                key, value = key_value_pair
                env_vars[key.strip()] = value.strip()
    
    except FileNotFoundError:
        return Exception(f"The file {file_path} does not exist.")
    except Exception as e:
        return e
    
    return env_vars


def main():
    """main function for self test"""
    pass
    # ChatAPI
    # chatapi = ChatAPI()  # remember_chat_history=False
    # answer = chatapi.chat("who are you?")
    # print(answer)

    # log = setup_logger(level=logging.DEBUG, log_file="logs/a.log")
    # log.info("Test log")
    # log.warning("Test warning")


if __name__ == "__main__":
    main()
