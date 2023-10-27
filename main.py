import os.path
import queue
import typing
import threading
from functools import partial

from pygame import mixer
from comment_spider.filters import BasicFilter
from llms.llms import ChatGLM
from digital_human import DigitalHuman
from assistant.assistants import BaseAssistant, Supervisor, MovementAssistant
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
        """
        self.digital_human = digital_human
        self.spider = spider
        self.assistants = assistants

    def start(self):
        spider_thread = threading.Thread(target=partial(self.spider.run))
        spider_thread.start()
        while True:
            if not comments_queue.empty():
                nickname, comment, dt = comments_queue.get()
                # response, _ = self.digital_human.reply(comment)
                response = "你也good!"
                print(nickname, comment, '\n回答：', response)
            else:
                self.digital_human.talk()


def main():
    comment_filter = BasicFilter(
        min_len=3,
        max_len=1000,
        exclude_sentences=[
            '来了',
            '送出了 ×'
        ]
    )
    glm = ChatGLM('http://127.0.0.1:8000')
    digital_human = DigitalHuman(glm, 'resources/scripts.txt')
    if not os.path.exists('vector_store'):
        digital_human.prepare_qa_datasource('resources/qa.csv')
    spider = DouyinLiveStreamSpider('305342780901', comments_queue, filter=comment_filter)
    movement_assistant = MovementAssistant(['q', 'w', 'e', 'a', 's', 'z', 'd', 'x'], [10, 15])
    supervisor = Supervisor('直播助手.exe')
    live_stream = LiveStream(digital_human, spider, [movement_assistant, supervisor])
    live_stream.start()


if __name__ == '__main__':
    main()
