import os
import queue

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
import sqlite3


class DouyinLiveStreamSpider:
    def __init__(self, room_id, comments_queue):
        self.room_id = room_id
        self.room_url = "https://live.douyin.com/" + room_id
        self.comments_list = set()
        self.comments_queue = comments_queue
        self.connection, self.cursor = self.init_db()
        self.driver = self.connect_browser()

    def init_db(self):
        connection = sqlite3.connect(f"{self.room_id}.db")
        cursor = connection.cursor()
        try:
            self.cursor.execute("CREATE TABLE comment_spider(nickname, comment)")
        except Exception as e:
            pass
        return connection, cursor

    def connect_browser(self, user_data_dir="D:/ChromeProfile"):
        # os.environ['PATH'] = os.environ['PATH'] + ';' + "C:/Program Files/Google/Chrome/Application"
        # os.system(f'chrome.exe --remote-debugging-port=9222 --user-data-dir="{user_data_dir}"')
        # 打开浏览器
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def crawl_comments(self):
        comments = self.driver.find_element(by=By.XPATH, value='//div[@class="webcast-chatroom___list"]')
        names = comments.find_elements(by=By.XPATH, value='.//span[@class="rc30lnLh"]')
        contents = comments.find_elements(by=By.XPATH, value='.//span[@class="b76LkBHq"]/span')
        if len(names) <= len(self.comments_list):
            return
        for nickname, content in zip(names, contents):
            try:
                nickname = nickname.text
                content = content.text
                if (nickname, content) not in self.comments_list:
                    self.comments_list.add((nickname, content))
                    print("%s 来了新评论：%s" % (nickname, content))
                    self.comments_queue.put((nickname, content))
                    self.cursor.execute("insert into comment_spider values (?, ?)", (nickname, content))
                    self.connection.commit()
            except Exception as e:
                pass

    def run(self):
        print(self.room_url)
        self.driver.get(self.room_url)
        while True:
            self.crawl_comments()


if __name__ == '__main__':
    cl = queue.Queue()
    spider = DouyinLiveStreamSpider("78480182181", cl)
    spider.run()
