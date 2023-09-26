#!/usr/bin/env python3
"""
utilities
"""
import json
import logging
import os
import re
from logging.handlers import RotatingFileHandler
from os import path

import requests

### Settings ###
LOG_LEVEL = logging.DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
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
    handler = RotatingFileHandler(log_file, maxBytes=1024000, backupCount=5)
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
                req_body = re.sub(b'(\r\n\r\n)(.*?)(\r\n--)',br'\1<binary raw data>\3', req_body,flags=re.DOTALL)
                req_body = req_body.decode('utf-8')
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
            url, data=data, headers=headers_new, files=files, verify=verify, timeout=(3.1, 60)
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
