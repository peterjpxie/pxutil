#!/usr/bin/env python3
"""
chat based on chatGPT API

Sample REST API
---------------
2023-03-04 04:20:10: -----------Request----------->
POST https://api.openai.com/v1/chat/completions

Content-Type: application/json
Authorization: Bearer <OPENAI_TOKEN>
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
import json
import os
from os import path

from .util import OPENAPI_TOKEN, post
# NB: 'from util' causes tox to fail with error: ModuleNotFoundError, which seems a bug of tox IMO. Avoid it for now.
# try: # when `python pxutil/chat.py`
#     from .util import OPENAPI_TOKEN, post
# except ImportError: # when `python chat.py` ImportError: attempted relative import with no known parent package
#     from util import OPENAPI_TOKEN, post

class ChatAPI:
    """
    chatGPT API
    """

    def __init__(
        self,
        url="https://api.openai.com/v1/chat/completions",
        token=OPENAPI_TOKEN,  # default to environment variable OPENAPI_TOKEN
        system_content=None,
        model="gpt-3.5-turbo",
    ):
        self.url = url
        assert token, "OpenAI token cannot be None."
        self.token = token
        self.model = model
        self.messages = []
        self.system_content = system_content
        if system_content:
            self.messages.append({"role": "system", "content": system_content})

    def chat(self, question: str, last_question=None, last_answer=None):
        """chat with a question and get an answer both in string format

        return: answer str or Exception
        """
        # add last chat message
        if last_question and last_answer:
            self.messages.append({"role": "user", "content": last_question})
            self.messages.append({"role": "assistant", "content": last_answer})

        self.messages.append({"role": "user", "content": question})
        payload = {
            "model": self.model,  # "gpt-3.5-turbo",
            "messages": self.messages,
        }
        # messages sample:
        #    "messages": [
        #        {"role": "system", "content": "You are a helpful assistant."}, # appreciation help get a better answer
        #        # {"role": "user", "content": "Who won the world series in 2020?"},
        #        ### assistant for context history
        #        # {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        #        # {"role": "user", "content": "Where was it played?"},
        #        {"role": "user", "content": "Write a python function for check prime number?"},
        #    ]

        headers = {"Authorization": "Bearer %s" % self.token}
        print('headers:', headers)
        # no indent for payload to save possible tokens
        resp = post(self.url, headers=headers, data=json.dumps(payload))  # , indent=4
        if isinstance(resp, Exception):
            return Exception("Chat API request failed with error: %s." % resp)

        if len(resp["choices"]) >= 1:
            for choice in resp["choices"]:
                if choice["index"] == 0 and choice["finish_reason"] in ("stop", None):
                    answer = choice["message"]["content"]
                    answer = answer.strip("\n").strip()
                    # chatlog_api.info("Answer: %s\n%s" % ("-" * 6 + ">", answer))
                    return answer

        return Exception(
            "Chat API request failed with no answer choices."
        )  # default if no answer is found in the response

if __name__ == "__main__":
    # self test
    chatapi = ChatAPI()
    # answer = chatapi.chat("Who won the world series in 2020?")
    answer = chatapi.chat("who are you?")
    print(answer)
