import queue
import threading
import time
from functools import partial

from llms.llms import ChatGLM
from digital_human import DigitalHuman
from comments.bilibili_spider import BilibiliLiveStreamSpider

comments_queue = queue.Queue()


class GrabThread(threading.Thread):

    def __init__(self, func, args=()):
        super(GrabThread, self).__init__()
        self.func = func
        self.args = args
        self.result = None

    def run(self):

        """run func registry by sub-class"""
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception as e:
            return str(e)


class LiveStream:
    def __init__(self, digital_human, spider: BilibiliLiveStreamSpider):
        self.digital_human = digital_human
        self.spider = spider

    def start(self):
        spider_thread = threading.Thread(target=partial(self.spider.run))
        spider_thread.start()
        print("111")
        while True:
            if not comments_queue.empty():
                comment = comments_queue.get()
                print(comment)
            print("...")
            time.sleep(3)


def main():
    glm = ChatGLM()
    digital_human = DigitalHuman(glm)
    spider = BilibiliLiveStreamSpider('22969536', comments_queue)
    live_stream = LiveStream(digital_human, spider)
    live_stream.start()


if __name__ == '__main__':
    main()
