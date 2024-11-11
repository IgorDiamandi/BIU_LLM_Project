from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding

embed_model = OpenAIEmbedding(embed_batch_size=42)

documents = SimpleDirectoryReader("../data/documents").load_data()


def create_index(documents):
    if not documents:
        print("Error: No documents to create embeddings. Please add documents to the 'data/documents/' directory.")
        return None

    index = VectorStoreIndex.from_documents(documents)
    return index


index = create_index(documents)


def retrieve(query, k=3):
    if index is None:
        return ["No documents available to retrieve information from."]

    query_engine = index.as_query_engine()
    response = query_engine.query(query)

    return [str(item) for item in response]
