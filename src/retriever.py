from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
import json
import os

embed_model = OpenAIEmbedding(embed_batch_size=42)
settings = Settings
settings.embed_model = embed_model

documents = []

# Load documents from JSON files in the specified directory
data_directory = 'data\documents\yehonatan'
for filename in os.listdir(data_directory):
    if filename.endswith(".json"):
        file_path = os.path.join(data_directory, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

                # Extract full_text and separate metadata
                text_content = data.get('full_text', '')  # Extract the actual content for embedding
                metadata = {key: value for key, value in data.items() if key != 'full_text'}  # Keep the rest as metadata

                # Create a Document with separated text and metadata
                if text_content:  # Ensure there's some text content to add
                    documents.append(Document(text=text_content, metadata=metadata))
                else:
                    print(f"Warning: Document in file {filename} has no 'full_text'. Skipping.")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {filename}: {e}")

# Function to create an index with an increased chunk size to accommodate larger metadata
def create_index(documents):
    if not documents:
        print("Error: No documents to create embeddings. Please add documents to the 'data/documents/' directory.")
        return None

    # Increase the chunk size to handle large metadata
    # We will use a very large chunk size to ensure all metadata fits
    index = VectorStoreIndex.from_documents(documents, settings=settings, chunk_size=8192)
    return index

index = create_index(documents)

# Retrieval function using the created index
def retrieve(query, k=3):
    if index is None:
        return ["No documents available to retrieve information from."]

    query_engine = index.as_query_engine()
    response = query_engine.query(query)

    # Convert response to a list of strings to return
    return [str(response)]
