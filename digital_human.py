import asyncio
import os
import time
import platform

from pygame import mixer
import edge_tts
import tempfile
from llms.llms import BaseLLM

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class DigitalHuman:

    def __init__(self, llm: BaseLLM, script_path: str):
        self.llm = llm
        self.speech_files = []
        self.prepare_speeches(script_path)
        self.answering_flag = False
        self.current_pos = 0
        self.current_file = self.speech_files[0]

    def prepare_speeches(self, script_path, path_type="audio"):
        if path_type == "audio":
            self.speech_files = [os.path.join(script_path, file) for file in os.listdir(script_path)]
        else:
            with open(script_path, encoding='utf-8') as f:
                for sentence in f.readlines():
                    fname = asyncio.run(self.tts(sentence))
                    self.speech_files.append(fname)

    def talk(self):
        if not mixer.music.get_busy():
            self.answering_flag = False
            # 继续上次talk的位置
            if self.current_pos > 0:
                mixer.music.load(self.current_file)
                mixer.music.play(start=self.current_pos // 1000, fade_ms=500)
                self.current_pos = 0
            else:
                current_file = self.speech_files[0]
                # 把第一个音频放到列表末尾
                del self.speech_files[0]
                self.speech_files.append(current_file)
                mixer.music.load(current_file)
                mixer.music.play()

    def reply(self, message: str, history=None) -> tuple:
        # response, history = self.llm.chat(message, history)
        response = "你好啊"
        fname = asyncio.run(self.tts(response))
        while mixer.music.get_busy() and self.answering_flag:
            time.sleep(0.5)
            continue
        if not self.answering_flag:
            mixer.music.pause()
            self.current_pos = mixer.music.get_pos()
        self.answering_flag = True
        mixer.music.load(fname)
        mixer.music.play()
        return response, history

    @staticmethod
    async def tts(message, voice="zh-CN-XiaoxiaoNeural"):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
            voice = edge_tts.Communicate(text=message, voice=voice, rate='-4%', volume='+0%')
            await voice.save(fp.name)
            return fp.name
