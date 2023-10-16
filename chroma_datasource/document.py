import os
import pandas as pd


class ChromaDocument:
    def __init__(self, document_content: str, metadata: dict, embedding=None, distance=0):
        self.document_content = document_content
        self.metadata = metadata
        self.embedding = embedding
        self.distance = distance

    def __str__(self):
        return """{
        content: %s
        metadata: %s
        distance: %f\n}""" % (
            self.document_content[:max(10, len(self.document_content))],
            self.metadata,
            self.distance
        )


class ChromaDocuments:
    next_id = 1000

    def __init__(self):
        self.documents = []
        self.metadatas = []
        self.distances = []
        self.ids = []

    @classmethod
    def from_texts(cls, text_path):
        text_documents = cls()
        filepaths = [os.path.join(text_path, file) for file in os.listdir(text_path)]
        for filepath in filepaths:
            with open(filepath, encoding='utf-8') as f:
                content = f.read().strip()
            document = ChromaDocument(content, {'source': os.path.basename(filepath)})
            text_documents.add([document])
        return text_documents

    @classmethod
    def from_csv(cls, csv_path, key='document'):
        csv_documents = cls()
        df = pd.read_csv(csv_path).head(100)
        documents = df[key]
        del df[key]
        metadatas = df.to_dict('records')
        for document, metadata in zip(documents, metadatas):
            document = ChromaDocument(document, metadata)
            csv_documents.add([document])
        return csv_documents

    @classmethod
    def from_jsonl(cls, jsonl_path, key='document'):
        pass

    @classmethod
    def from_query_results(cls, query_results):
        result_documents = cls()
        for document, metadata, distance in zip(
                query_results['documents'][0],
                query_results['metadatas'][0],
                query_results['distances'][0]
        ):
            document = ChromaDocument(document, metadata, distance=distance)
            result_documents.add([document])
        return result_documents

    def to_document_list(self):
        document_list = []
        for document, metadata, distance in zip(self.documents, self.metadatas, self.distances):
            document_list.append(ChromaDocument(document, metadata, distance=distance))
        return document_list

    def add(self, documents: list[ChromaDocument]):
        for document in documents:
            self.documents.append(document.document_content)
            self.metadatas.append(document.metadata)
            self.ids.append(f"id{self.next_id}")
            self.distances.append(document.distance)
            self.next_id += 1

    def clear(self):
        self.documents.clear()
        self.metadatas.clear()
        self.ids.clear()
