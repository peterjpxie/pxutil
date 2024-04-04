#!/usr/bin/env python3
"""
Some handy utilities from Peter Jiping Xie  
"""
# __all__ = ['bash','trim_docstring','grep']


import sys
import re
import os
import json
import logging
from logging.handlers import RotatingFileHandler
from os import path
import os.path as ospath
from contextlib import contextmanager

import requests

### Settings ###
# util should only print log in DEBUG level
LOG_LEVEL = logging.ERROR  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FOLDER = "logs"
VALID_HTTP_RESP = (200, 201, 202)


# root_path is parent folder of this file
root_path = path.dirname(path.abspath(__file__))
# create log folder if not exist
os.makedirs(path.join(root_path, LOG_FOLDER), exist_ok=True)

# %(levelname)7s to align 7 bytes to right, %(levelname)-7s to left.
common_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)-7s][%(module)s][%(lineno)-3d]: %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S",
)


# Note: To create multiple log files, must use different logger name.
def setup_logger(log_file, level=logging.INFO, name="", formatter=common_formatter):
    """Function setup as many loggers as you want."""
    # handler = logging.FileHandler(log_file, mode="w")  # default mode is append
    # Or use a rotating file handler
    handler = RotatingFileHandler(log_file, maxBytes=1024000, backupCount=2)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


# default debug logger
debug_log_filename = path.join(root_path, LOG_FOLDER, "debug.log")
log = setup_logger(debug_log_filename, LOG_LEVEL, "debug")

# logger for API outputs
api_formatter = logging.Formatter(
    "%(asctime)s: %(message)s", datefmt="%Y-%m-%d %I:%M:%S"
)
api_outputs_filename = path.join(root_path, LOG_FOLDER, "api.log")
apilog = setup_logger(api_outputs_filename, LOG_LEVEL, "api", formatter=api_formatter)


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


def pretty_print_request_json(request):
    """pretty print request in json format if possible, otherwise print in text or bytes
    Note it may differ from the actual request as it is pretty formatted.

    Params
    ------
    request:   requests' request object
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

    apilog.debug(
        "{}\n{}\n\n{}\n\n{}\n".format(
            "-----------Request----------->",
            request.method + " " + request.url,
            "\n".join(f"{k}: {v}" for k, v in request.headers.items()),
            req_body,
        )
    )


def pretty_print_response_json(response):
    """pretty print response in json format
    If failing to parse body in json format, print in text.

    Params
    ------
    response:   requests' response object
    """
    try:
        resp_data = response.json()
        resp_body = json.dumps(resp_data, indent=4)
    # if .json() fails, ValueError is raised, take text format
    except ValueError:
        resp_body = response.text

    apilog.debug(
        "{}\n{}\n\n{}\n\n{}\n".format(
            "<-----------Response-----------",
            "Status code:" + str(response.status_code),
            "\n".join(f"{k}: {v}" for k, v in response.headers.items()),
            resp_body,
        )
    )


def post(url, data=None, headers={}, files=None, verify=True, amend_headers=True):
    """
    Common request post function with below features, which you only need to take care of url and body data:
        - append common headers (when amend_headers=True)
        - print request and response in API log file
        - Take care of request exception and non-20x response codes and return None, so you only need to care normal json response.
        - arguments are the same as requests.post, except amend_headers.

    verify: False - Disable SSL certificate verification

    Return: response dict or Exception
    """

    # append common headers if none
    headers_new = headers
    if amend_headers is True:
        headers_new["Content-Type"] = "application/json"
        # headers_new["Authorization"] = "Bearer %s" % self.token

    # send post request
    try:
        # timeout in sec to avoid waiting on unreachable server, ref: https://requests.readthedocs.io/en/latest/user/advanced/#timeouts
        resp = requests.post(
            url,
            data=data,
            headers=headers_new,
            files=files,
            verify=verify,
            timeout=(3.1, 60),
        )
    except Exception as ex:
        log.error("requests.post() failed with exception: %s" % ex)
        return ex

    # pretty request and response into API log file
    # Note: request print is common as it could be a JSON body or a normal text
    pretty_print_request_json(resp.request)
    pretty_print_response_json(resp)

    if resp.status_code not in VALID_HTTP_RESP:
        error = "requests.post() failed with response code %s." % resp.status_code
        log.error(error)
        return Exception(error)

    try:
        return resp.json()
    except ValueError:
        error = "requests.post() failed to parse response body in JSON format."
        log.error(error)
        return Exception(error)


def bash(cmd, encoding=None):
    """
    subprocess.run with intuitive options to execute system commands just like shell bash command.

    Inspired by https://pypi.org/project/bash/.

    cmd: string
    return: CompletedProcess object in text (decode as locale encoding), with attributes stdout, stderr and returncode.

    Usage example:
    ret = bash('ls')
    print(ret.stdout, ret.stderr, ret.returncode)

    Warning of using shell=True: https://docs.python.org/3/library/subprocess.html#security-considerations
    """
    from subprocess import run, PIPE  # Popen, CompletedProcess
    import sys
    import locale

    if sys.version_info >= (
        3,
        7,
    ):  # version_info is actually a tuple, so compare with a tuple
        if encoding:
            return run(
                cmd, shell=True, capture_output=True, text=True, encoding=encoding
            )
        else:
            return run(cmd, shell=True, capture_output=True, text=True)

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


def replace_in_file(files, old, new, backup=None):
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
    if not ospath.isfile(path):
        raise FileNotFoundError(f"Failed to import as file {path} does not exist.")

    with prepend_sys_path(ospath.dirname(path)):
        module_name = ospath.splitext(ospath.basename(path))[0]
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
        "model": "gpt-3.5-turbo", # gpt-4
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
        model="gpt-3.5-turbo",  # gpt-4 etc.
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

        if len(resp["choices"]) >= 1:
            for choice in resp["choices"]:
                if choice["index"] == 0 and choice["finish_reason"] in ("stop", None):
                    answer = choice["message"]["content"]
                    answer = answer.strip("\n").strip()
                    # record chat history
                    if self.remember_chat_history:
                        self.chat_history.append({"role": "user", "content": question})
                        self.chat_history.append(choice["message"])
                    return answer

        return Exception(
            "Chat API request failed with no answer choices."
        )  # default if no answer is found in the response


def list_module_contents(module_name: str):
    ''' List contents of a module/package: submodules, classes, and functions.
    '''
    import inspect, pkgutil, importlib
    # add CWD to sys.path if not already in, to support modules in CWD when run anywhere as CLI script px.listmod
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
    try:
        # Import the module based on the provided name
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        print(f"Module '{module_name}' not found.")
        return

    print(f"Listing contents of module: {module_name}")

    # Try to list submodules if it is a package
    print("\nSubmodules:")
    if hasattr(module, "__path__"):   # Check if module is a package
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

def main():
    """main function for self test"""
    # ChatAPI
    chatapi = ChatAPI()  # remember_chat_history=False
    answer = chatapi.chat("who are you?")
    print(answer)
    # answer = chatapi.chat("how old are you?")
    # print(answer)


if __name__ == "__main__":
    main()
