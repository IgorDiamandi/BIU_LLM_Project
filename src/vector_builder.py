import os
import json
from pinecone import Pinecone, ServerlessSpec
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Document
from config.config_helper import pinecone_api_key, openai_api_key
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken

# Initialize tokenizer for the embedding model
tokenizer = tiktoken.encoding_for_model("text-embedding-ada-002")
MAX_TOKENS = 4096

# Initialize Pinecone and OpenAI clients
pc = Pinecone(api_key=pinecone_api_key)
client = OpenAIEmbedding(openai_api_key=openai_api_key)


# Function to split text into chunks
def chunk_text(text, max_tokens=MAX_TOKENS, overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_tokens,
        chunk_overlap=overlap,
        
        # separators=["\n\n", "\n", ".", " "]
        separators=["\n\n", "\n"]
    )
    return text_splitter.split_text(text)


# Function to clean metadata
def clean_metadata(metadata):
    cleaned_metadata = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)):
            cleaned_metadata[key] = value
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            cleaned_metadata[key] = value
    return cleaned_metadata


# Create and configure Pinecone index
def initialize_index(index_name="biullmindex"):
    if index_name in pc.list_indexes().names():
        pc.delete_index(name=index_name)
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    return pc.Index(index_name)


# Function to add documents to Pinecone
def add_documents_to_pinecone(documents, pinecone_index):
    for i, doc in enumerate(documents):
        metadata = clean_metadata(doc.metadata)
        if len(tokenizer.encode(doc.text)) > MAX_TOKENS:
            chunks = chunk_text(doc.text)
            for j, chunk in enumerate(chunks):
                chunk_id = f"doc-{i}-chunk-{j}"
                embedding = client.get_text_embedding(chunk)
                pinecone_index.upsert(
                    vectors=[(chunk_id, embedding, {**metadata, "chunk_id": chunk_id})]
                )
        else:
            embedding = client.get_text_embedding(doc.text)
            pinecone_index.upsert(
                vectors=[(f"doc-{i}", embedding, metadata)]
            )


# Main function to populate the database
def populate_vector_db(data_path, index_name="biullmindex"):
    pinecone_index = initialize_index(index_name)
    documents = []
    for filename in os.listdir(data_path):
        print(f'Populating {filename}')
        if filename.endswith(".json"):
            file_path = os.path.join(data_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                text_content = data.get('full_text', '')
                
                metadata_keys = ['course_name', 'summary']
                metadata = {key: value for key, value in data.items() if key in metadata_keys}
           
                if text_content:
                    documents.append(Document(text=text_content, metadata=metadata))
                    
    add_documents_to_pinecone(documents, pinecone_index)


json_path = os.path.abspath(os.path.join('..', 'data', 'documents', 'eng'))
print("JSONs docs path:", json_path)

populate_vector_db(json_path, index_name="biullmindex")