import os.path
import random
import time
from queue import Queue
from datetime import datetime

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
import sqlite3

from comment_spider.filters import BaseFilter, BasicFilter


class BaseLiveStreamSpider:
    def __init__(
            self,
            room_id: int | str,
            domain: str,
            comments_queue: Queue,
            persist_path=".",
            remote_port=9222,
            filter=None
    ):
        self.room_id = room_id
        self.domain = domain
        if domain.endswith('/'):
            self.room_url = domain + room_id
        else:
            self.room_url = domain + "/" + room_id
        self.persist_path = f"{persist_path}/{room_id}.db"
        self.remote_port = remote_port
        self.filter = filter
        self.comments_list = set()
        self.comments_queue = comments_queue
        self.connection, self.cursor = self.init_db()
        self.driver = self.connect_browser()

    def init_db(self):
        if not os.path.exists(os.path.dirname(self.persist_path)):
            os.makedirs(os.path.dirname(self.persist_path))
        connection = sqlite3.connect(self.persist_path, check_same_thread=False)
        cursor = connection.cursor()
        try:
            cursor.execute("CREATE TABLE comment_spider(nickname, comment, datetime)")
        except Exception as e:
            # print(traceback.print_exc())
            pass
        return connection, cursor

    def connect_browser(self):
        # 打开浏览器
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.remote_port}")
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def crawl_comments(self):
        raise NotImplementedError("请实现crawl_comments方法")

    def filter_comments(self, comments):
        if not self.filter:
            return comments
        return self.filter.clean(comments)

    def run(self):
        print("直播间地址：", self.room_url)
        self.driver.get(self.room_url)
        time.sleep(3)
        while True:
            self.crawl_comments()


class BilibiliLiveStreamSpider(BaseLiveStreamSpider):

    def __init__(self, room_id: int | str, comments_queue: Queue, persist_path=".",
                 remote_port=9222, filter=None):
        super().__init__(room_id, 'https://live.bilibili.com/', comments_queue, persist_path, remote_port, filter)
        self.name_ids = []

    def crawl_comments(self):
        container = self.driver.find_element(by=By.XPATH, value='//div[@id="chat-items"]')
        chat_items = container.find_elements(by=By.XPATH, value='.//div[contains(@class, "chat-item")]')
        # 过滤已有评论
        new_comments = [item for item in chat_items if item.id not in self.name_ids]
        self.name_ids.extend([item.id for item in new_comments])
        if len(new_comments) == 0:
            return
        # for nickname, content in zip(names, contents):
        for item in chat_items:
            nickname = item.get_attribute('data-uname').strip()
            content = item.get_attribute('data-danmaku').strip()
            # nickname = nickname.text.strip()
            # content = content.text.strip()
            # 过滤评论内容
            content = self.filter_comments([content])
            if content:
                content = content[0]
            else:
                return
            dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("%s 来了新评论：%s" % (nickname, content))
            self.comments_queue.put((nickname, content, dt))
            self.cursor.execute(
                "insert into comment_spider values (?, ?, ?)",
                (nickname, content, dt)
            )
            self.connection.commit()


class DouyinLiveStreamSpider(BaseLiveStreamSpider):

    def __init__(self, room_id: int | str, comments_queue: Queue, persist_path=".",
                 remote_port=9222, filter=None):
        super().__init__(room_id, 'https://live.douyin.com/', comments_queue, persist_path, remote_port, filter)
        self.name_ids = []

    def crawl_comments(self):
        comments = self.driver.find_element(by=By.XPATH, value='//div[@class="webcast-chatroom___list"]')
        names = comments.find_elements(by=By.XPATH, value='.//span[@class="rc30lnLh"]')
        contents = comments.find_elements(by=By.XPATH, value='.//span[@class="b76LkBHq"]/span')
        # 过滤已有评论
        new_comments = list(zip(
            *[[name, content] for name, content in zip(names, contents) if name.id not in self.name_ids]))
        if new_comments:
            names, contents = new_comments
        else:
            names, contents = [], []
        self.name_ids.extend([name.id for name in names])
        if len(names) == 0:
            return
        for nickname, content in zip(names, contents):
            nickname = nickname.text
            content = content.text
            # 过滤评论内容
            content = self.filter_comments([content])
            if content:
                content = content[0]
            else:
                return
            dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # print("%s 来了新评论：%s" % (nickname, content))
            self.comments_queue.put((nickname, content, dt))
            self.cursor.execute(
                "insert into comment_spider values (?, ?, ?)",
                (nickname, content, dt)
            )
            self.connection.commit()


class MeituanSpider(BaseLiveStreamSpider):
    def __init__(self, room_id: int | str, comments_queue: Queue, persist_path=".",
                 remote_port=9222, filter=None):
        super().__init__(room_id, 'https://live.douyin.com/', comments_queue, persist_path, remote_port, filter)
        self.name_ids = []
        self.room_url = "https://live.meituan.com/#/"

    def crawl_comments(self):
        names = self.driver.find_elements(by=By.XPATH,
                                          value='//div[@class="list-item"]//span[contains(@class, "user-name")]')
        contents = self.driver.find_elements(by=By.XPATH, value='//div[@class="list-item"]//span[@class="content"]')
        # 过滤已有评论
        new_comments = list(zip(
            *[[name, content] for name, content in zip(names, contents) if name.id not in self.name_ids]))
        if new_comments:
            names, contents = new_comments
        else:
            names, contents = [], []
        self.name_ids.extend([name.id for name in names])
        if len(names) == 0:
            return
        for nickname, content in zip(names, contents):
            nickname = nickname.text
            content = content.text
            print(nickname, content)
            # 过滤评论内容
            content = self.filter_comments([content])
            if content:
                content = content[0]
            else:
                continue
            dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.comments_queue.put((nickname, content, dt))
            self.cursor.execute(
                "insert into comment_spider values (?, ?, ?)",
                (nickname, content, dt)
            )
            self.connection.commit()

    def run(self):
        print("直播间地址：", self.room_url)
        self.driver.get(self.room_url)
        time.sleep(3)
        while True:
            self.crawl_comments()


if __name__ == '__main__':
    exclude_sentences = [
        '来了',
        '送出了'
    ]
    q = Queue()
    spider = MeituanSpider('30857154', q, filter=None)
    spider.run()
