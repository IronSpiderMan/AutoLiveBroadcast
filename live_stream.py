import typing
import threading
from functools import partial

from digital_human import DigitalHuman
from assistant.assistants import BaseAssistant
from comment_spider.spiders import BaseLiveStreamSpider


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
        global comments_queue
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


if __name__ == '__main__':
    from llms.llms import NotLLM
    from settings import SCRIPTS

    print(SCRIPTS)
    # llm = NotLLM()
    # digital_human = DigitalHuman(llm, SCRIPTS)
    # live_stream = LiveStream()
