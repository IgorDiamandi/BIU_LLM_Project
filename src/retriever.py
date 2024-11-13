import os
import json
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.embeddings.openai import OpenAIEmbedding


# Set up the embedding model for use with LlamaIndex
embed_model = OpenAIEmbedding(embed_batch_size=42)

# Load JSON documents from the directory
documents = []
data_directory = "./data/documents"

for filename in os.listdir(data_directory):
    if filename.endswith(".json"):
        file_path = os.path.join(data_directory, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file, strict=False)
                # Attempt to create a document, skipping if there's missing required data
                if 'full_text' in data:
                    documents.append(Document(text=data['full_text'], metadata=data))
                else:
                    print(f"Skipping file {filename} due to missing 'full_text' field.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {filename}: {e}")

# Create the settings that includes the embedding model
settings = Settings
settings.embed_model = embed_model


def create_index(documents):
    if not documents:
        print("Error: No documents to create embeddings. Please add documents to the 'data/documents/' directory.")
        return None

    # Create the vector index from the documents using the settings
    index = VectorStoreIndex.from_documents(documents, settings=settings)
    return index


# Create the index
index = create_index(documents)


# Define the retrieve function
def retrieve(query):
    if index is None:
        return ["No documents available to retrieve information from."]

    # Create the query engine from the index
    query_engine = index.as_query_engine()
    response = query_engine.query(query)  # Use k to specify the number of results to retrieve

    # Return the response
    return [response.response] if response else ["No relevant documents found."]
