# Table of Contents

* [pxutil.pxutil](#pxutil.pxutil)
  * [normal\_path](#pxutil.pxutil.normal_path)
  * [CustomFormatter](#pxutil.pxutil.CustomFormatter)
  * [setup\_logger](#pxutil.pxutil.setup_logger)
  * [pretty\_json](#pxutil.pxutil.pretty_json)
  * [pretty\_print\_request\_json](#pxutil.pxutil.pretty_print_request_json)
  * [pretty\_print\_response\_json](#pxutil.pxutil.pretty_print_response_json)
  * [post](#pxutil.pxutil.post)
  * [request](#pxutil.pxutil.request)
  * [bash](#pxutil.pxutil.bash)
  * [bashx](#pxutil.pxutil.bashx)
  * [grep](#pxutil.pxutil.grep)
  * [replace\_in\_file](#pxutil.pxutil.replace_in_file)
  * [time2seconds](#pxutil.pxutil.time2seconds)
  * [purge](#pxutil.pxutil.purge)
  * [exit\_on\_exception](#pxutil.pxutil.exit_on_exception)
  * [is\_running\_foreground](#pxutil.pxutil.is_running_foreground)
  * [register\_signal\_ctrl\_c](#pxutil.pxutil.register_signal_ctrl_c)
  * [set\_work\_path](#pxutil.pxutil.set_work_path)
  * [prepend\_sys\_path](#pxutil.pxutil.prepend_sys_path)
  * [import\_any](#pxutil.pxutil.import_any)
  * [ChatAPI](#pxutil.pxutil.ChatAPI)
    * [chat](#pxutil.pxutil.ChatAPI.chat)
  * [list\_module\_contents](#pxutil.pxutil.list_module_contents)
  * [read\_dotenv](#pxutil.pxutil.read_dotenv)
  * [is\_text\_file](#pxutil.pxutil.is_text_file)
  * [token\_counter](#pxutil.pxutil.token_counter)

<a id="pxutil.pxutil"></a>

# pxutil.pxutil

Some handy utilities from Peter Jiping Xie

<a id="pxutil.pxutil.normal_path"></a>

#### normal\_path

```python
def normal_path(path: str, resolve_symlink=False)
```

return a normalized path

**Arguments**:

- `resolve_symlink` - resolve symbolic link to the actual path
  
  calls os.path.x:
- `expanduser` - ~/a.txt => /home/user/a.txt
- `expandvars` - '$HOME/mydir' => /home/user/mydir
- `normpath` - /usr/local//../bin/ => /usr/bin
- `realpath` - a.txt => /home/user/project/a.txt (full path);  /usr/local/bin/python3 (symlink) => /usr/bin/python3.8
- `abspath` - a.txt => /home/user/project/a.txt (full path); /usr/local/bin/python3 (symlink) => /usr/local/bin/python3;
  /usr/local//../bin/ => /usr/bin
  
- `Note` - abspath does half realpath + normpath.

<a id="pxutil.pxutil.CustomFormatter"></a>

## CustomFormatter Objects

```python
class CustomFormatter(logging.Formatter)
```

Custom formatter to truncate module name to N characters.

<a id="pxutil.pxutil.setup_logger"></a>

#### setup\_logger

```python
def setup_logger(level=logging.INFO,
                 log_file=None,
                 name=__name__,
                 formatter=None,
                 formatter_simple_time_only=False,
                 mode="a",
                 rotate=True,
                 maxBytes=1024000,
                 backup_count=5)
```

Set up a logger with console or rotating file output.

**Arguments**:

- `level` - Logging level.
- `log_file` _str_ - Path to the log file (path will be auto normalized), or None
  for console logging.
- `name` _str_ - Logger name. NB: To create multiple log files, must use
  different logger name.
- `formatter` - logging.Formatter object. If None, use
  formatter_simple_time_only if true, otherwise use the default
  formatter.
- `formatter_simple_time_only` - If True and formatter is None, use
- `logging.Formatter("%(asctime)s` - %(message)s").
- `mode` - File open mode if rotate is False, 'w' for write, 'a' for
  append (default).
- `rotate` _boolean_ - Whether to rotate log file.
- `maxBytes` - maxBytes for rotating file handler.
- `backup_count` - backup_count for rotating file handler.
  

**Returns**:

  The logger object.

<a id="pxutil.pxutil.pretty_json"></a>

#### pretty\_json

```python
def pretty_json(json_str)
```

return pretty formatted json string if possible, otherwise return the original

**Arguments**:

- `json_str` - The input could be anything, e.g., bytes, and it just returns the original if it is not a valid json string.

<a id="pxutil.pxutil.pretty_print_request_json"></a>

#### pretty\_print\_request\_json

```python
def pretty_print_request_json(request, logger)
```

pretty print request in json format if possible, otherwise print in text or bytes
Note it may differ from the actual request as it is pretty formatted.

**Arguments**:

- `request` - requests' request object.
- `logger` - logging instance.

<a id="pxutil.pxutil.pretty_print_response_json"></a>

#### pretty\_print\_response\_json

```python
def pretty_print_response_json(response, logger)
```

pretty print response in json format
If failing to parse body in json format, print in text.

**Arguments**:

- `response` - requests' response object.
- `logger` - logging instance.

<a id="pxutil.pxutil.post"></a>

#### post

```python
def post(url,
         *,
         data=None,
         headers={},
         files=None,
         verify=True,
         amend_headers=True,
         content_type=None,
         session=None,
         logger=None,
         **kwargs)
```

shorthand for request('POST', ...)

<a id="pxutil.pxutil.request"></a>

#### request

```python
def request(method: str,
            url: str,
            *,
            data=None,
            headers={},
            files=None,
            auth=None,
            verify=True,
            amend_headers=True,
            content_type=None,
            session=None,
            logger=None,
            **kwargs)
```

Send a request with common helpers, for any HTTP method.

Features:
- append common headers (when amend_headers=True)
- print request and response in API log file
- Take care of request exception and error response codes (>=400) and return None, so you only need to care normal json response.
- arguments are the same as requests.request, except amend_headers.

**Arguments**:

- `method` - Same as requests.request.
- `url` - Same as requests.request.
- `data` - Same as requests.request. NA for GET.
- `headers` - Same as requests.request.
- `files` - Same as requests.request.
- `auth` - Same as requests.request. NA for POST.
- `verify` - Same as requests.request. False disables SSL certificate
  verification, e.g. to test a dev server with self-signed
  certificate.
- `amend_headers` - Append common headers, e.g. set Content-Type to
  "application/json" if body is json. NA for GET.
- `content_type` - Set header Content-Type if provided.
- `session` - requests.Session() instance; send requests in the provided
  session if set, and maintain session cookies.
- `logger` - logging instance, e.g. logging.getLogger(), to pretty log API
  request and response in INFO level (please set proper level in the
  logger). Default to None, no logging.
- `**kwargs` - Other arguments requests.request takes.
  

**Returns**:

  Response decoded as dict if possible, decoded text if not json,
  original bytes if decoding fails (not likely), '' if response has no
  body, or Exception if any error or response code >=400.

<a id="pxutil.pxutil.bash"></a>

#### bash

```python
def bash(cmd: str, encoding=None)
```

subprocess.run with intuitive options to execute system commands just like shell bash command.

Inspired by https://pypi.org/project/bash/.

**Arguments**:

- `cmd` - command in a string, e.g. 'ls -l'
- `encoding` - encoding to decode output, e.g. 'utf-8'. Auto detected if None.
  

**Returns**:

  CompletedProcess object in text (decode as locale encoding), with attributes stdout, stderr and returncode.
  

**Example**:

  ret = bash('ls')
  print(ret.stdout, ret.stderr, ret.returncode)
  
  Warning of using shell=True: https://docs.python.org/3/library/subprocess.html#security-considerations

<a id="pxutil.pxutil.bashx"></a>

#### bashx

```python
def bashx(cmd, x=True, e=False)
```

run system cmd like bash -x

Print the cmd with + prefix before executing
Don't capture the output or error

**Arguments**:

- `cmd` - string - command to run
- `x` - When True, print the command with prefix + like shell 'bash -x' before running it
- `e` - When True, exit the python program when returncode is not 0, like shell 'bash -e'.
  

**Returns**:

  CompletedProcess object with only returncode.
  

**Notes**:

  You can set the following environment variables which have the same effect of but overwrite argument options.
  BASH_CMD_PRINT=True     same as x=True
  BASH_EXIT_ON_ERROR=True same as e=True
  

**Example**:

  ret = bashx('ls')
  print(ret.returncode)
  
  Warning of using shell=True: https://docs.python.org/3/library/subprocess.html#security-considerations

<a id="pxutil.pxutil.grep"></a>

#### grep

```python
def grep(pattern, string=None, filename=None)
```

simulate linux grep command

return lines matching a pattern in a string or a file.

**Arguments**:

- `pattern` - regular expression string
  

**Example**:

  result = grep('keyword', filename='a.txt' )
  for i in result:
  print(i)
  

**Notes**:

  If the matched list is too big, you can modify it to use yield generator.

<a id="pxutil.pxutil.replace_in_file"></a>

#### replace\_in\_file

```python
def replace_in_file(files, old, new, backup="")
```

Replace in place directly on a file.

**Arguments**:

- `files` - single or list of files, e.g. 'a.txt' or ['a.txt',]
- `old` - old string to replace
- `new` - new string
- `backup` - backup file suffix, e.g. '.bak'. None means no backup

<a id="pxutil.pxutil.time2seconds"></a>

#### time2seconds

```python
def time2seconds(time)
```

delta time string to number of seconds

**Arguments**:

- `time` - e.g. '2d' for 2 days, supported units: d-day, h-hour, m-minute, s-second
  

**Returns**:

  integer number of seconds
  
- `Note` - Month and year duration varies. Not worth doing for the sake of simplicity.

<a id="pxutil.pxutil.purge"></a>

#### purge

```python
def purge(dir, age="0s", filename_filter="*")
```

Purge files and subfolders older than certain age

**Arguments**:

- `dir` - directory to purge files and subfolders
- `age` - e.g. '2h', support d-day, h-hour, m-minute, s-second
- `filename_filter` - glob format, e.g. debug.log*
  

**Example**:

  purge('/root/tmp/', '24h', 'debug.log*')
  

**Notes**:

  It retains the parent folder dir. Use shutil.rmtree if you want to remove the folder as well.

<a id="pxutil.pxutil.exit_on_exception"></a>

#### exit\_on\_exception

```python
def exit_on_exception(func)
```

Decorator to exit if func returns an exception(error)

<a id="pxutil.pxutil.is_running_foreground"></a>

#### is\_running\_foreground

```python
def is_running_foreground()
```

Check if current script is running in foreground

**Examples**:

  python a.py : True
  python a.py & : False
  python a.py > a.log : True
  python a.py | tee a.log : True
  nohup python a.py & : False
  nohup python a.py : False (* special case, this is considered as background as input is ignored and output is redirected. - to reconsider as it is running in foreground.)
  
- `ref` - https://stackoverflow.com/questions/24861351/how-to-detect-if-python-script-is-being-run-as-a-background-process

<a id="pxutil.pxutil.register_signal_ctrl_c"></a>

#### register\_signal\_ctrl\_c

```python
def register_signal_ctrl_c()
```

Register signal handler for ctrl+c

<a id="pxutil.pxutil.set_work_path"></a>

#### set\_work\_path

```python
@contextmanager
def set_work_path(path)
```

With statement to set the cwd within the context

**Arguments**:

- `path` - The path string to the cwd. Note this path will be automatically normalized by normal_path().
  

**Yields**:

  cwd path string
  

**Example**:

  with set_work_path('./tmp') as p:
  os.system('ls')

<a id="pxutil.pxutil.prepend_sys_path"></a>

#### prepend\_sys\_path

```python
@contextmanager
def prepend_sys_path(path)
```

With statement to prepend path to sys.path within the context

**Arguments**:

- `path` - The path string to prepend. Note this path will be automatically normalized by normal_path().
  

**Yields**:

  normalized path string
  

**Example**:

  with prepend_sys_path('./tmp') as p:
  import this_module

<a id="pxutil.pxutil.import_any"></a>

#### import\_any

```python
def import_any(path: str)
```

import any module from a path regardless of sys.path

It will automatically prepend the parent directory of path to sys.path if not already in, and remove it after import.

**Arguments**:

- `path` - path to a module, e.g., ./config/a.py, /home/user/config/a.py
  

**Returns**:

  imported module
  

**Example**:

  a = import_any('./config/a.py')
  a.func()

<a id="pxutil.pxutil.ChatAPI"></a>

## ChatAPI Objects

```python
class ChatAPI()
```

chat based on chatGPT API

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

<a id="pxutil.pxutil.ChatAPI.chat"></a>

#### chat

```python
def chat(question: str)
```

Ask a question and get an answer

**Returns**:

  answer str or Exception

<a id="pxutil.pxutil.list_module_contents"></a>

#### list\_module\_contents

```python
def list_module_contents(module_name: str)
```

List contents of a module/package: submodules, classes, and functions.

<a id="pxutil.pxutil.read_dotenv"></a>

#### read\_dotenv

```python
def read_dotenv(file_path=".env")
```

Reads a .env file (ini file w/o section header) and returns a dict of environment variables like os.environ.

**Arguments**:

- `file_path` - str, path to the .env file.
  

**Returns**:

  dict with key-value pairs of environment variables or Exception if any.
  Note it is all string values. And return empty dict {} if no environment variables set.

<a id="pxutil.pxutil.is_text_file"></a>

#### is\_text\_file

```python
def is_text_file(filepath: str, blocksize=512)
```

Check if a file is a text file.
Reads a block of the file and tries to decode it as UTF-8.
If decoding succeeds, consider it text.

<a id="pxutil.pxutil.token_counter"></a>

#### token\_counter

```python
def token_counter(text: str)
```

retun number of tokens counted by tiktoken

