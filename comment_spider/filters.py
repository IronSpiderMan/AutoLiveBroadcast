import re
import difflib
from functools import partial


class BaseFilter:
    def _clean(self, text):
        """
        文本清洗函数，如果需要自定义Filter需要继承BaseFilter，实现_clean方法，完成清洗。如果当前句子需要丢弃，则返回None
        :param text: 需要清洗的文本
        :return: 清洗后的文本，如果返回None表示丢弃该文本
        """
        raise NotImplementedError()

    def clean(self, texts):
        cleaned_comments = list(map(partial(self._clean), texts))
        return [x for x in cleaned_comments if x is not None]


class BasicFilter(BaseFilter):
    def __init__(
            self,
            comment_regex=r'.*?',
            min_len=5,
            max_len=30,
            stop_words=None,
            exclude_sentences=None,
            allow_special_token=None
    ):
        """
        :param comment_regex: 文本内容需要匹配的模式
        :param min_len: 最小长度，低于这个长度的文本会被过滤
        :param max_len: 最大长度，高于这个长度的文本会被过滤
        :param stop_words: 违禁词，list或文件路径，包含违禁词的句子会被过滤
        :param exclude_sentences: 排除句，与排除句非常相似的句子（difflib的ratio >= 0.95）会被过滤
        :param allow_special_token:
        """
        self.comment_regex = comment_regex
        self.min_len = min_len
        self.max_len = max_len
        if not stop_words:
            self.stop_words = []
        elif not isinstance(stop_words, list):
            with open(stop_words, encoding='utf-8') as f:
                self.stop_words = f.readlines()
        else:
            self.stop_words = stop_words
        if not isinstance(exclude_sentences, list):
            with open(exclude_sentences, encoding='utf-8') as f:
                self.exclude_sentences = f.readlines()
        else:
            self.exclude_sentences = exclude_sentences
        self.allow_special_token = allow_special_token

    def _clean(self, comment):
        if not re.search(self.comment_regex, comment):
            print('不符合设定的模式：', comment)
            return None
        if len(comment) < self.min_len or len(comment) > self.max_len:
            print('长度太长或太短：', comment)
            return None
        for stop_word in self.stop_words if self.stop_words else []:
            if comment.__contains__(stop_word):
                print("包含违禁词：", comment)
                return None
        for exclude_sentence in self.exclude_sentences:
            ratio = difflib.SequenceMatcher(None, exclude_sentence, comment).ratio()
            if ratio >= 0.95:
                print('疑似为排除句：', comment)
                return None
        return comment


class DouyinFilter(BaseFilter):
    pass


if __name__ == '__main__':
    fn = BasicFilter(r'.*', min_len=1, exclude_sentences=['不好'])
    print(fn.clean(['你好', '你不好']))
