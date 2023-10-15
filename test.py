# 语音识别
# from transformers import WhisperProcessor, WhisperForConditionalGeneration
# from datasets import load_dataset
#
# processor = WhisperProcessor.from_pretrained("openai/whisper-medium")
# model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-medium")
# model.config.forced_decoder_ids = None
# ds = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
# # print(ds[0]['audio'])
# sample = ds[0]["audio"]
# input_features = processor(sample["array"], sampling_rate=sample["sampling_rate"], return_tensors="pt").input_features
# predicted_ids = model.generate(input_features)
# transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
# print(transcription)

# ChatGLM对话

import os
import requests
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
from vectorizer import load_embedding_model
from vectorizer import store_chroma


def chat(prompt, history=None):
    payload = {
        "prompt": prompt, "history": [] if not history else history
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(

        url='http://127.0.0.1:8000',
        json=payload,
        headers=headers
    ).json()
    return resp['response'], resp['history']


history = [
    [
        '基于下面的资料回答问题，如果提供的资料不足以回答问题，则回复“不知道”。下面是资料：\n1. "当然，对我们这些懂得生活的人来说，我们才不在乎那些编号呢！我真愿意像讲童话那样来开始这个故事，我真想这样开头：“从前，有一个小王子，他住在一个和他身体差不多大的星球上，他渴望拥有一个朋友……”对懂得生活的人来说，这样说就可能显得更加真实。"\n2. "就这样，我认识了小王子。\n\n  \n第三章\n\n    我花了好长时间才明白他是从哪里来的。小王子问我很多问题，我有很多疑惑，可是，对我提出的问题，小王子好像压根儿没有听见似的。一点一点的，偶然间他无意中吐露的一些只言片语逐渐使我搞清了他的来历。例如，当他第一次看见我的飞机时我就不画出我的飞机了，因为这种图画对我来说太复杂，他问我道：“这是个什么玩意儿呀？”\n\n    “这不是玩意儿。它能飞。这是飞机，是我的飞机。”"\n3. "就像这样，要是你对他们说：“小王子存在的证据就是他非常漂亮，他笑着，想要一只羊。如果有人想要一只绵羊，那就是他存在的证明。”这样告诉他们的结果是什么呢？他们一定会耸耸肩膀，不以为然，把你当作小孩子看待。但是，如果你对他们说“小王子来自的星球就是小行星612”，那么他们就十分信服，就不会提出一大堆问题来和你纠缠。\n\n    他们就是这样的。一定不要因为这样去攻击他们，小孩子们对大人们应该宽厚些。"\n4. "我当时很骄傲地告诉他我能飞。他听到后疑惑地大声说：“什么！你是从天上掉下来的？”\n\n    “是的。”我谦逊地答道。\n\n    “哦！这真不可思议。”\n\n    此时小王子可爱地笑了起来。这让我很生气。我不希望自己严肃的痛苦受到别人嘲笑。然后，他又说道：“那么，你也是从天上来的了！你是哪个星球上的？”\n\n    这时，我忽然有点明白他为什么会在这里，对于他神秘出现这个费解的秘密，我隐约发现了一点线索。于是，我中断了他的提问，迫不及待地问道：“你是从另一个星球上来的吗？”"\n\n下面是你要回答的问题："小王子可能来自哪个星球"',
        '小王子来自的星球是小行星612。'
    ],
    [
        '基于下面的资料回答问题，如果提供的资料不足以回答问题，则回复“不知道”。下面是资料：\n1. "“再见。”狐狸说，“喏，这就是我的秘密。很简单：只有用心才能看得清。重要的东西，用眼睛是看不见的。”\n\n    “重要的东西，用眼睛是看不见的。”小王子重复着这句话，以便能把它记在心间。\n\n    “正因为你为你的玫瑰花费了时间，这才使你的玫瑰变得如此重要。”\n\n    “正因为我为我的玫瑰花费了时间……”小王子又重复着，要使自己记住这些。\n\n    “人们已经忘记了这个道理，”狐狸说，“可是，你不应该忘记它。你现在要对你驯服过的一切负责到底。你要对你的玫瑰负责……”"\n2. "“我是一只狐狸。”狐狸说。\n\n    “来和我一起玩吧？”小王子建议，“我是如此的悲伤……”\n\n    “我不能和你一起玩，”狐狸说，“我还没有被驯服呢。”\n\n    “啊！真对不起。”小王子说。\n\n    思索了一会儿，他又说道：\n\n    “什么叫驯服呀？”\n\n    “你不是这里人。”狐狸说，“你来寻找什么？”\n\n    “我来找人。”小王子说，“什么叫驯服呢？”\n\n    “人，”狐狸说，“他们有枪，他们还打猎，这真碍事！他们也饲养鸡，这些就是他们全部兴趣，你是来寻找鸡的吗？”"\n3. "“我有点明白了。”小王子说，“有一朵花……我想，她把我驯服了……”\n\n    “这是可能的。”狐狸说，“地球上什么样的事都可能看到……”\n\n    “哦，这不是在地球上的事。”小王子说。\n\n    狐狸感到迷惑，但却十分好奇。\n\n    “在另一个星球上？”\n\n    “是的。”\n\n    “在那个星球上，有猎人吗？”\n\n    “没有。”\n\n    “这很有意思。那么，有鸡吗？”\n\n    “没有。”\n\n    “没有十全十美的。”狐狸叹息地说道。\n\n    狐狸又把话题拉回来："\n4. "狐狸久久地看着小王子。\n\n    “请你驯服我吧！”他说。\n\n    “我是很愿意的。”小王子回答道，“可我的时间不多了。我还要去寻找朋友，还有许多事物要了解。”\n\n    “只有被驯服了的事物，才会被了解。”狐狸说，“人再也不会花时间去了解任何东西的。他们总是到商店那里去购买现成的东西。因为世界上还没有购买朋友的商店，所以人也就没有朋友。如果你想要一个朋友，那就驯服我吧！”\n\n    “那么我应当做些什么呢？”小王子说。"\n\n下面是你要回答的问题："狐狸告诉小王子的秘密是什么？"',
        '狐狸告诉小王子的秘密是：“只有用心才能看得清。重要的东西，用眼睛是看不见的。”'
    ]
]

embeddings = load_embedding_model()

if not os.path.exists('VectorStore'):
    loader = TextLoader('resources/little-prince.txt', encoding='utf-8')
    documents = loader.load()
    text_spliter = CharacterTextSplitter(chunk_size=256, chunk_overlap=0)
    split_docs = text_spliter.split_documents(documents)
    db = store_chroma(split_docs, embeddings)
else:
    db = Chroma(persist_directory='VectorStore', embedding_function=embeddings)
while True:
    query = input("Human: ")
    similar_docs = db.similarity_search(query, include_metadata=True, k=4)
    prompt = "基于下面给出的资料，回答问题。如果资料不足，回答不了，就回复不知道。下面是资料：\n"
    for idx, doc in enumerate(similar_docs):
        prompt += f"{idx + 1}. {doc.page_content}\n"
    prompt += f"下面是问题：{query}"
    print(prompt)
    response, _ = chat(prompt, [])
    print("Bot: ", response)
