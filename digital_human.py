import asyncio
import os
import random
import time
import platform

from pygame import mixer
from tqdm import tqdm
import edge_tts
import tempfile
from llms.llms import BaseLLM, ChatGLM, NotLLM
from chroma_datasource.document import ChromaDocuments
from chroma_datasource.chroma_utils import ChromaDatasource

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class DigitalHuman:

    def __init__(
            self,
            llm: BaseLLM,
            script_path: str,
            persis_path='vector_store',
            embedding_model_name="shibing624/text2vec-base-chinese",
            qa_collection_name="qa_pairs",
            speech_path="resources/speeches",
            path_type="script",
    ):
        self.llm = llm
        self.speech_files = []
        self.answering_flag = False
        self.current_pos = 0
        self.qa_collection_name = qa_collection_name
        self.speech_path = speech_path
        self.prepare_speeches(script_path, path_type)
        self.current_file = self.speech_files[0]
        self.qa_datasource = ChromaDatasource(persis_path, embedding_model_name)

    def prepare_speeches(self, script_path, path_type="script"):
        """
        准备需要朗读的脚本文件，或者音频目录。
        :param script_path: 脚本文件路径或者音频目录
        :param path_type: 路径类型，audio表示音频目录
        :return:
        """
        if path_type == "audio":
            self.speech_files = [os.path.join(script_path, file) for file in os.listdir(script_path)]
        else:
            if os.listdir(self.speech_path):
                self.speech_files = [
                    os.path.join(self.speech_path, file)
                    for file in os.listdir(self.speech_path)
                ]
                self.speech_files.sort(key=lambda x: os.path.getctime(x))
                return
            with open(script_path, encoding='utf-8') as f:
                sentences = f.readlines()
                bar = tqdm(total=len(sentences))
                for sentence in sentences:
                    fname = asyncio.run(self.tts(sentence))
                    self.speech_files.append(fname)
                    bar.update(1)

    def prepare_qa_datasource(self, qa_path: str):
        """
        :param qa_path: qa问答路径。可以是txt文件夹路径（暂不支持）、csv文件路径、jsonl文件路径（暂不支持）
        csv文件要求有document、answer字段
        :return:
        """
        self.qa_datasource.reset()
        self.qa_datasource.create_collection(self.qa_collection_name)
        if os.path.isdir(qa_path):
            documents = ChromaDocuments.from_texts(qa_path)
        elif qa_path.endswith('.csv'):
            documents = ChromaDocuments.from_csv(qa_path)
        else:
            documents = None
        assert isinstance(documents, ChromaDocuments)
        self.qa_datasource.add(documents, self.qa_collection_name)

    def talk(self):
        """
        自动循环朗读脚本内容，或者提供的音频文件。
        :return:
        """
        if not mixer.music.get_busy():
            self.answering_flag = False
            # 继续上次talk的位置
            if self.current_pos > 0:
                mixer.music.load(self.current_file)
                mixer.music.play(start=self.current_pos // 1000, fade_ms=500)
                self.current_pos = 0
            else:
                current_file = random.choice(self.speech_files)
                # current_file = self.speech_files[0]
                # # 把第一个音频放到列表末尾
                # del self.speech_files[0]
                # self.speech_files.append(current_file)
                mixer.music.load(current_file)
                mixer.music.play()

    def reply(self, message: str, history=None, distance_threshold=0.05) -> tuple:
        """
        回复评论内容
        :param message: 评论内容
        :param history: 历史对话，暂不提供
        :param distance_threshold: 距离阈值。当查询结果距离小于等于该阈值时，返回问答，否则调用llm
        :return:
        """
        if not isinstance(history, list):
            history = []
        query_results = self.qa_datasource.query(message, self.qa_collection_name, 1)
        query_result = ChromaDocuments.from_query_results(query_results).to_document_list()[0]
        if query_result.distance <= distance_threshold:
            response = query_result.metadata['answer']
        else:
            prompt = f'请简短地回答："{message}"'
            response, history = self.llm.chat(prompt, history)
        if not response:
            return response, history
        fname = asyncio.run(self.tts(response, save_path='tmp'))
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
    async def tts(message, voice="zh-CN-XiaoxiaoNeural", save_path="resources/speeches"):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False, dir=save_path) as fp:
            voice = edge_tts.Communicate(text=message, voice=voice, rate='-4%', volume='+0%')
            await voice.save(fp.name)
            return fp.name


if __name__ == '__main__':
    mixer.init()
    # digital_human = DigitalHuman(NotLLM(), 'resources/scripts.txt')
    digital_human = DigitalHuman(NotLLM(), 'resources/speeches', path_type='audio')
    digital_human.prepare_qa_datasource('resources/qa.csv')
    while True:
        digital_human.talk()
        # question = input("人：")
        # resp, _ = digital_human.reply(question, [], distance_threshold=0.1)
        # print(resp)
