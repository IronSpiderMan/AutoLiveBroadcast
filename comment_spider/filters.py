import re
import difflib
from functools import partial


class BaseFilter:
    def __init__(
            self,
            comment_regex=r'$.*$',
            min_len=5,
            max_len=30,
            stop_words=None,
            exclude_sentences=None,
            allow_special_token=None
    ):
        self.comment_regex = comment_regex
        self.min_len = min_len
        self.max_len = max_len
        self.stop_words = stop_words
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

    def clean(self, comments):
        cleaned_comments = list(map(partial(self._clean), comments))
        return [x for x in cleaned_comments if x is not None]


class DouyinFilter(BaseFilter):
    pass


if __name__ == '__main__':
    fn = BaseFilter(r'.*', min_len=1, exclude_sentences=['不好'])
    print(fn.clean(['你好', '你不好']))
