from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
import sqlite3


class BilibiliLiveStreamSpider:
    def __init__(self, room_id):
        self.room_id = room_id
        self.room_url = "https://live.bilibili.com/" + room_id
        self.comments_list = set()
        self.connection, self.cursor = self.init_db()
        self.driver = self.connect_browser()

    def init_db(self):
        connection = sqlite3.connect(f"{self.room_id}.db")
        cursor = connection.cursor()
        try:
            self.cursor.execute("CREATE TABLE comments(nickname, comment)")
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
        container = self.driver.find_element(by=By.XPATH, value='//div[@id="chat-items"]')
        comments = container.find_elements(by=By.XPATH, value='.//div[contains(@class, "chat-item")]')
        if len(comments) <= len(self.comments_list):
            return
        for comment in comments:
            try:
                nickname = comment.find_element(
                    by=By.XPATH,
                    value='.//span[contains(@class, "user-name")]'
                ).text.strip().split()[0]
                content = comment.find_element(
                    by=By.XPATH,
                    value='.//span[contains(@class, "danmaku-item-right")]'
                ).text.strip()
                if (nickname, content) not in self.comments_list:
                    self.comments_list.add((nickname, content))
                    print("%s 来了新评论：%s" % (nickname, content))
                    self.cursor.execute("insert into comments values (?, ?)", (nickname, content))
                    self.connection.commit()
            except Exception as e:
                pass

    def run(self):
        print(self.room_url)
        self.driver.get(self.room_url)
        while True:
            self.crawl_comments()


if __name__ == '__main__':
    spider = BilibiliLiveStreamSpider("26357658")
    spider.run()
