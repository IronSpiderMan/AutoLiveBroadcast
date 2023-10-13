from llms.llms import BaseLLM


class DigitalHuman:

    def __init__(self, llm: BaseLLM):
        self.llm = llm

    def talk(self):
        pass

    def reply(self, message: str, history=None) -> tuple:
        response, history = self.llm.chat(message, history)
        return response, history
