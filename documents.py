from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter


def load_documents(filepath, chunk_size=256, chunk_overlap=0):
    loader = TextLoader(filepath, encoding='utf-8')
    documents = loader.load()
    text_spliter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    split_docs = text_spliter.split_documents(documents)
    return split_docs
