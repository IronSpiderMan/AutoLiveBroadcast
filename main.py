from digital_human import DigitalHuman
from llms.llms import ChatGLM


class LiveStream:
    def __init__(self, digital_human, spider):
        self.digital_human = digital_human
        self.spider = spider

    def start(self):
        pass


def main():
    glm = ChatGLM()
    digital_human = DigitalHuman(glm)


if __name__ == '__main__':
    main()
