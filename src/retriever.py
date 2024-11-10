from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

Settings.embed_model = OpenAIEmbedding()

documents = SimpleDirectoryReader("../data/documents").load_data()

index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("query string")
embed_model = OpenAIEmbedding(embed_batch_size=42)
