import edge_tts
import tempfile
from llms.llms import BaseLLM


class DigitalHuman:

    def __init__(self, llm: BaseLLM):
        self.llm = llm

    def talk(self):
        pass

    def reply(self, message: str, history=None) -> tuple:
        response, history = self.llm.chat(message, history)
        return response, history

    @staticmethod
    async def tts(message, voice="zh-CN-XiaoxiaoNeural"):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
            voice = edge_tts.Communicate(text=message, voice=voice, rate='-4%', volume='+0%')
            await voice.save(fp.name)
            return fp.name
