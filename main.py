import queue
import typing
import threading
from functools import partial

from pygame import mixer
from settings import *
from comment_spider.filters import BasicFilter
from llms.llms import ChatGLM, NotLLM
from digital_human import DigitalHuman
from assistant.assistants import BaseAssistant, Supervisor, MovementAssistant, CustomAssistant
from comment_spider.spiders import BaseLiveStreamSpider, DouyinLiveStreamSpider

comments_queue = queue.Queue()
mixer.init()


class LiveStream:
    def __init__(
            self,
            digital_human: DigitalHuman,
            spider: BaseLiveStreamSpider,
            assistants: typing.List[BaseAssistant]
    ):
        """
        直播
        :param digital_human: 数字人，负责朗读脚本，回复评论
        :param spider: 负责爬取评论
        :param assistants: 助手，协助直播。负责监管评论、直播状态等
        """
        self.digital_human = digital_human
        self.spider = spider
        self.assistants = assistants

    def start(self):
        if self.spider:
            spider_thread = threading.Thread(target=partial(self.spider.run))
            spider_thread.start()
        for assistant in self.assistants:
            assistant.start()
        while True:
            if not comments_queue.empty():
                nickname, comment, dt = comments_queue.get()
                response, _ = self.digital_human.reply(comment)
                if not response:
                    continue
                print(nickname, comment, '\n回答：', response)
            else:
                self.digital_human.talk()


def main():
    llm = NotLLM()
    digital_human = DigitalHuman(
        llm,
        SCRIPTS,
        QA_PERSIST,
        EMBEDDING_MODEL_NAME,
        QA_COLLECTION_NAME,
        speech_path=SPEECHES
    )
    try:
        print("正在载入问答库...")
        digital_human.prepare_qa_datasource(QA_PATH)
        print("载入问答库成功...")
    except Exception:
        print("问答库已存在...")
    spider = SpiderCls(ROOM_ID, comments_queue, COMMENTS_PERSIST, filter=None)
    live_stream = LiveStream(
        digital_human,
        spider,
        []
    )
    live_stream.start()


if __name__ == '__main__':
    main()
