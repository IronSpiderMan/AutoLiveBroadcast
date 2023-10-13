import os
import time
import asyncio
import requests
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
import edge_tts
from pygame import mixer
from langchain.llms import ChatGLM
from vectorizer import load_embedding_model, store_chroma
from documents import load_documents


def chat_api(prompt, history=None):
    payload = {
        "prompt": prompt, "history": list(history)
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(
        url="127.0.0.1:8000",
        json=payload,
        headers=headers
    )
    return resp['response'], resp['history']


def create_qa_chain(embeddings, document_path):
    # 加载数据库
    if not os.path.exists('VectorStore'):
        documents = load_documents(document_path)
        db = store_chroma(documents, embeddings)
    else:
        db = Chroma(persist_directory='VectorStore', embedding_function=embeddings)
    # 创建llm
    llm = ChatGLM(
        endpoint='http://127.0.0.1:8000',
        max_token=80000,
        top_p=0.9
    )
    # 创建qa
    retriever = db.as_retriever()
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type='stuff',
        retriever=retriever,
    )
    return qa


# 初始化音频
mixer.init()

# chrome.exe --remote-debugging-port=9222 --user-data-dir="D:\ChromeProfile"
# mixer.init(devicename='Speakers (High Definition Audio Device)')

# 保存聊天记录
message_queue = []
answered_queue = []

# # 创建qa
# embeddings = load_embedding_mode('text2vec3')
# qa = create_qa_chain(embeddings, 'tmp/output.txt')

# 打开浏览器
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)
comments = driver.find_element(by=By.XPATH, value='//div[@id="danmu-interactive"]')


async def tts(sentence):
    voice = edge_tts.Communicate(text=sentence, voice='zh-CN-XiaoxiaoNeural', rate='-4%', volume='+0%')
    fname = f"tmp/{time.time()}.mp3"
    await voice.save(fname)
    while mixer.music.get_busy():
        time.sleep(1)
        continue
    mixer.music.load(fname)
    mixer.music.play()


def chat(prompt, history):
    resp = requests.post(
        url='http://127.0.0.1:8000',
        json={"prompt": prompt, "history": history},
        headers={"Content-Type": "application/json;charset=utf-8"}
    )
    return resp.json()['response'], resp.json()['history']


def chat_with_document(prompt, history):
    response = qa.run(prompt)
    print(response)
    return response


def reply(driver, message):
    enter = driver.find_element(by=By.XPATH, value='//input[@class="n-input__input-el"]')
    enter.send_keys(message)
    driver.find_element(by=By.XPATH,
                        value='//button[@class="n-button n-button--primary-type n-button--medium-type ml-10px"]').click()


time.sleep(5)
while True:
    names = comments.find_elements(by=By.XPATH, value='.//div/span[@class="user-name"]')
    contents = comments.find_elements(by=By.XPATH, value='.//div/span[@class="msg-content"]')
    # 添加新消息
    for name, content in zip(names, contents):
        name = name.text
        content = content.text
        if (name, content) in message_queue + answered_queue or name == "新建文件夹X：":
            continue
        else:
            message_queue.append((name, content))
            print("新消息", name, content)
    # 取出最近消息
    if message_queue:
        current_message = message_queue[0]
        answered_queue.append(current_message)
        del message_queue[0]
        name, content = current_message
        print("当前回答：", content)
        response, _ = chat(content, [])
        # response = qa.run(content)
        print("ChatGLM：", response)
        asyncio.run(tts(response))
        # reply(driver, f"@{name}{response}")
    else:
        time.sleep(3)
