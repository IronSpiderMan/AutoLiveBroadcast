import requests


class BaseLLM:
    def chat(self, message, history):
        raise NotImplemented()


class ChatGLM(BaseLLM):
    def __init__(self, url="http://127.0.0.1:8000"):
        self.url = url

    def chat(self, prompt, history=None):
        payload = {
            "prompt": prompt, "history": [] if not history else history
        }
        headers = {"Content-Type": "application/json"}
        resp = requests.post(
            url=self.url,
            json=payload,
            headers=headers
        ).json()
        return resp['response'], resp['history']
