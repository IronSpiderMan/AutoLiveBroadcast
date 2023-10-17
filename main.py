import queue
import threading
from functools import partial

from pygame import mixer
from llms.llms import ChatGLM
from digital_human import DigitalHuman
# from comment_spider.bilibili_spider import BilibiliLiveStreamSpider
from comment_spider.spiders import BilibiliLiveStreamSpider

comments_queue = queue.Queue()
mixer.init()


class LiveStream:
    def __init__(self, digital_human: DigitalHuman, spider: BilibiliLiveStreamSpider):
        self.digital_human = digital_human
        self.spider = spider

    def start(self):
        spider_thread = threading.Thread(target=partial(self.spider.run))
        spider_thread.start()
        while True:
            if not comments_queue.empty():
                nickname, comment = comments_queue.get()
                response, _ = self.digital_human.reply(comment)
                print(nickname, comment, response)
            else:
                self.digital_human.talk()


def main():
    glm = ChatGLM()
    digital_human = DigitalHuman(glm, 'little-prince')
    spider = BilibiliLiveStreamSpider('31063149', comments_queue)
    live_stream = LiveStream(digital_human, spider)
    live_stream.start()


if __name__ == '__main__':
    main()
