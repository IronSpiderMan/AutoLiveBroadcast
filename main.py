import os.path
import queue
import threading
from functools import partial

from pygame import mixer
from comment_spider.filters import BaseFilter
from llms.llms import ChatGLM
from digital_human import DigitalHuman
from comment_spider.spiders import BaseLiveStreamSpider, DouyinLiveStreamSpider

comments_queue = queue.Queue()
mixer.init()


class LiveStream:
    def __init__(self, digital_human: DigitalHuman, spider: BaseLiveStreamSpider):
        self.digital_human = digital_human
        self.spider = spider

    def start(self):
        spider_thread = threading.Thread(target=partial(self.spider.run))
        spider_thread.start()
        while True:
            if not comments_queue.empty():
                nickname, comment = comments_queue.get()
                response, _ = self.digital_human.reply(comment)
                print(nickname, comment, '\n回答：', response)
            else:
                self.digital_human.talk()


def main():
    comment_filter = BaseFilter(
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
    spider = DouyinLiveStreamSpider('886327984997', comments_queue, filter=comment_filter)
    live_stream = LiveStream(digital_human, spider)
    live_stream.start()


if __name__ == '__main__':
    main()
