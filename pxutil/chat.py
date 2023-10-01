#!/usr/bin/env python3
"""
chat based on chatGPT API

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
import json
import os


# add .pxutil.post to pxutil/__init__.py so it can be imported as `from pxutil import post` both outside and inside pxutil package
from pxutil import post
# NB: 'from util' causes tox to fail with error: ModuleNotFoundError, which seems a bug of tox IMO. Avoid it for now.
# try: # when `python pxutil/chat.py`
#     from .pxutil import post
# except ImportError: # when `python chat.py` ImportError: attempted relative import with no known parent package
#     from pxutil import post

# get TOKEN from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)

class ChatAPI:
    """
    chatGPT API
    """

    def __init__(
        self,
        url="https://api.openai.com/v1/chat/completions",
        token=OPENAI_API_KEY,  # default to environment variable OPENAI_API_KEY
        system_msg=None,
        model="gpt-3.5-turbo",
        remember_chat_history=True,
    ):
        self.url = url
        assert token, "OpenAI token cannot be None."
        self.token = token
        self.model = model
        self.system_msg = system_msg
        self.remember_chat_history = remember_chat_history
        self.chat_history = [] # list of past chat messages


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
            messages.extend(self.chat_history)
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


if __name__ == "__main__":
    # self test
    chatapi = ChatAPI() # remember_chat_history=False
    answer = chatapi.chat("who are you?")
    print(answer)
    # answer = chatapi.chat("how old are you?")
    # print(answer)
