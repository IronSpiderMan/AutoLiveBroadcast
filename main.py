import queue
import typing
import threading
from functools import partial

from pygame import mixer
from comment_spider.filters import BasicFilter
from llms.llms import ChatGLM
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
        # spider_thread = threading.Thread(target=partial(self.spider.run))
        # spider_thread.start()
        for assistant in self.assistants:
            assistant.start()
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
    try:
        print("正在载入问答库...")
        digital_human.prepare_qa_datasource('resources/qa.csv')
        print("载入问答库成功...")
    except Exception:
        print("问答库已存在...")
    spider = DouyinLiveStreamSpider('304725661518', comments_queue, filter=comment_filter)
    movement_assistant = MovementAssistant(['q', 'w', 'e', 'a', 's', 'z', 'd', 'x'], [10, 15])
    customer = CustomAssistant(spider.driver, comments_queue)
    supervisor = Supervisor('直播助手.exe')
    live_stream = LiveStream(
        digital_human, spider,
        [
            movement_assistant,
            supervisor,
            customer
        ]
    )
    live_stream.start()


if __name__ == '__main__':
    main()
