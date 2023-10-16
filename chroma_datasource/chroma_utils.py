from chromadb import PersistentClient, Settings
from chromadb.utils.embedding_functions import HuggingFaceEmbeddingFunction
from chroma_datasource.document import ChromaDocuments


class ChromaDatasource:
    def __init__(self, persist_path, model_name="shibing624/text2vec-base-chinese"):
        self.client = PersistentClient(persist_path, Settings(allow_reset=True))
        self.embedding_fn = HuggingFaceEmbeddingFunction(
            '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',
            model_name=model_name
        )

    def is_exist(self, collection_name):
        collection_names = [collection.name for collection in self.client.list_collections()]
        if collection_name in collection_names:
            return True
        else:
            return False

    def reset(self):
        self.client.reset()

    def create_collection(self, name):
        return self.client.create_collection(
            name,
            metadata={"hnsw:space": "cosine"},
            embedding_function=self.embedding_fn
        )

    def delete_collection(self, name):
        self.client.delete_collection(name)

    def get_collection(self, name):
        return self.client.get_collection(name)

    def add(self, documents: ChromaDocuments, collection_name):
        collection = self.get_collection(collection_name)
        collection.add(
            documents=documents.documents,
            metadatas=documents.metadatas,
            ids=documents.ids
        )

    def query(self, query, collection_name, n_results=3):
        collection = self.get_collection(collection_name)
        return collection.query(
            query_texts=[query],
            n_results=n_results,
        )


if __name__ == '__main__':
    documents = ChromaDocuments.from_texts('texts')
    datasource = ChromaDatasource('vector_store', 'shibing624/text2vec-base-chinese')
    datasource.delete_collection('qa_pairs')
    qa_pairs = datasource.create_collection('qa_pairs')
    datasource.add(documents, 'qa_pairs')

    datasource.is_exist('')

    # results = datasource.query('我吃饭呢', 'qa_pairs', 1)
    # print(results)
    # results = ChromaDocuments.from_query_results(results).to_document_list()
    # for result in results:
    #     print(result)
