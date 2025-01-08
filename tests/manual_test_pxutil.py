"""
manual tests for the unreliable tests.

usage:
pytest tests/manual_test_pxutil.py
"""
import platform
import os
import io
import sys
import pytest
import os.path as osp
import json
import time

import pxutil as px


def test_request():
    """test request"""
    from pxutil import request
    import requests

    # Test GET request
    get_url = "https://httpbin.org/get"
    response = request("GET", get_url)
    assert isinstance(response, dict)
    assert response["url"] == get_url

    # Test POST request with JSON data and headers
    post_url = "https://httpbin.org/post"
    json_data = {"key": "value"}
    headers = {"My-Header": "value"}
    response = request("POST", post_url, data=json.dumps(json_data), headers=headers)
    assert isinstance(response, dict)
    assert response["json"] == json_data
    assert response["headers"]["My-Header"] == "value"

    ## Test session with cookies
    # Create a Session object to persist cookies
    session = requests.Session()

    set_cookie_url = "https://httpbin.org/cookies/set/sessioncookie/123456789"
    get_cookies_url = "https://httpbin.org/cookies"

    # Set a cookie
    # This url will redirect to get_cookies_url while setting the cookies, we don't need that so set allow_redirects=False.
    response = request("GET", set_cookie_url, session=session, allow_redirects=False)
    assert isinstance(response, Exception) is False

    # Make another request to check cookies persistence
    # get_cookies_url will return cookies in the request as json body response
    response = request("GET", get_cookies_url, session=session)
    assert response == {"cookies": {"sessioncookie": "123456789"}}


def test_post():
    """test post, a shorthand of request"""
    from pxutil import post

    # Test POST request with JSON data and headers
    post_url = "https://httpbin.org/post"
    json_data = {"key": "value"}
    headers = {"My-Header": "value"}
    response = post(post_url, data=json.dumps(json_data), headers=headers)
    assert isinstance(response, dict)
    assert response["headers"]["My-Header"] == "value"
