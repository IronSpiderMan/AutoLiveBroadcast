import time
import random
import pythoncom
from typing import List
from threading import Thread

import wmi
import pytesseract
from PIL import ImageGrab

from pynput import keyboard


class BaseAssistant(Thread):
    def __init__(self):
        super().__init__()

    def run(self) -> None:
        self.func()

    def func(self):
        raise NotImplementedError()


class MovementAssistant(BaseAssistant):
    def __init__(self, actions: List, time_range: List[int]):
        super().__init__()
        # ['q', 'w', 'e', 'a', 's', 'z', 'd', 'x']
        self.actions = actions
        self.time_range = time_range
        self.kb = keyboard.Controller()

    def func(self):
        while True:
            with self.kb.pressed(keyboard.Key.ctrl):
                with self.kb.pressed(keyboard.Key.shift):
                    key = random.choice(self.actions)
                    self.kb.press(key)
                    self.kb.release(key)
            timestep = random.randrange(*self.time_range)
            time.sleep(timestep)


class Supervisor(BaseAssistant):
    def __init__(self, process_name, timestep=5):
        super().__init__()
        # 直播助手.exe
        self.process_name = process_name
        self.timestep = timestep

    def func(self):
        while True:
            im = ImageGrab.grab()
            # 识别文字
            string = pytesseract.image_to_string(im, lang='chi_sim')
            string = "".join(string.split())
            print(string)
            if string.__contains__("违规处罚") or string.__contains__("直播已中断") or string.__contains__(
                    "直播已结束"):
                pythoncom.CoInitialize()
                c = wmi.WMI()
                for process in c.Win32_Process(Name=self.process_name):
                    try:
                        process.Terminate()
                    except Exception:
                        pass
                print("监管到直播间被系统检测违规，关闭直播伴侣，停止监管...")
                break
            time.sleep(self.timestep)


class CustomAssistant(BaseAssistant):
    def __init__(self, driver, comment_queue):
        super().__init__()
        self.driver = driver
        self.comment_queue = comment_queue

    def func(self):
        pass


if __name__ == '__main__':
    supervisor = Supervisor("直播伴侣.exe")
    supervisor.start()
    supervisor.join()
