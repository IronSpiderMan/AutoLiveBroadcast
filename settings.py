import json
import os.path
import sys
from comment_spider.spiders import *
from llms.llms import *

BASE_PATH = sys.path[0]
with open('config.json', encoding='utf-8') as f:
    config = json.load(f)

# 爬虫
SPIDERS = {
    "douyin": DouyinLiveStreamSpider,
    "meituan": MeituanSpider,
    "bilibili": BilibiliLiveStreamSpider
}

# LLMs
LLMs = {
    "ChatGLM": ChatGLM,
    "NotLLM": NotLLM
}

# 资源文件路径
STOP_WORDS = os.path.join(BASE_PATH, config['resources']['stop_words'])
EXCLUDED_SENTENCES = os.path.join(BASE_PATH, config['resources']['excluded_sentences'])
COMMENTS_PERSIST = os.path.join(BASE_PATH, config['resources']['comment_persist'])
QA_PATH = os.path.join(BASE_PATH, config['resources']['qa_path'])
QA_PERSIST = os.path.join(BASE_PATH, config['resources']['qa_persist'])
SPEECHES = os.path.join(BASE_PATH, config['resources']['speeches_path'])
SCRIPTS = os.path.join(BASE_PATH, config['resources']['script_path'])

# chroma
QA_COLLECTION_NAME = config['chroma']['qa_collection_name']
EMBEDDING_MODEL_NAME = config['chroma']['embedding_model_name']

# classes
LlmCls = LLMs[config['digital_human']['llm']]
SpiderCls = SPIDERS[config['live_stream']['platform']]

# LiveStream
ROOM_ID = config['live_stream']['room_id']
