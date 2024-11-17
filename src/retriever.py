import os
import json
from pinecone import Pinecone, ServerlessSpec
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Document
from config.config_helper import pinecone_api_key, openai_api_key
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter


# Initialize tokenizer for the embedding model
tokenizer = tiktoken.encoding_for_model("text-embedding-ada-002")  # Replace with your model name if different
MAX_TOKENS = 4096  # Define the maximum token limit for the model

pc = Pinecone(api_key=pinecone_api_key)
client = OpenAIEmbedding(openai_api_key=openai_api_key)


def chunk_text(text, max_tokens=MAX_TOKENS, overlap=200):
    """
    Splits text into chunks, ensuring they respect the token limit while maintaining sentence and paragraph structure for better context preservation.
    """
    # Use LangChain's RecursiveCharacterTextSplitter for smart chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_tokens,  # Maximum size of each chunk
        chunk_overlap=overlap,  # Number of overlapping tokens
        separators=["\n\n", "\n", ".", " "]  # Priority separators for splitting
    )
    chunks = text_splitter.split_text(text)
    return chunks



# Check if the index exists and recreate it with the correct dimension
index_name = "biullmindex"
if index_name in pc.list_indexes().names():
    print(f"Deleting existing index: {index_name}")
    pc.delete_index(name=index_name)

print(f"Creating new index: {index_name} with dimension 1536")
pc.create_index(
    name=index_name,
    dimension=1536,  # Update to match the embedding vector size
    metric="cosine",  # Use cosine similarity (or 'dotproduct' / 'euclidean' based on your use case)
    spec=ServerlessSpec(
        cloud="aws",  # Replace with the cloud provider from your environment
        region="us-east-1"  # Replace with the region from your environment
    )
)

# Connect to the new index
pinecone_index = pc.Index(index_name)
# Initialize embedding model
embed_model = OpenAIEmbedding(embed_batch_size=42)

# Load documents from JSON files in the specified directory
documents = []
data_directory = 'data\\documents\\yehonatan\\1linejsons'
for filename in os.listdir(data_directory):
    if filename.endswith(".json"):
        file_path = os.path.join(data_directory, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

                # Extract full_text and separate metadata
                text_content = data.get('full_text', '')  # Extract the actual content for embedding
                metadata = {key: value for key, value in data.items() if
                            key != 'full_text'}  # Keep the rest as metadata

                # Create a Document with separated text and metadata
                if text_content:  # Ensure there's some text content to add
                    documents.append(Document(text=text_content, metadata=metadata))
                else:
                    print(f"Warning: Document in file {filename} has no 'full_text'. Skipping.")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {filename}: {e}")


def generate_embedding(text):
    print("Generating embedding")
    # Check if the text exceeds the token limit
    if len(tokenizer.encode(text)) > MAX_TOKENS:
        print("Text exceeds token limit. Splitting into chunks.")
        chunks = chunk_text(text)
        # Generate embeddings for each chunk
        embeddings = [client.get_text_embedding(chunk) for chunk in chunks]
        # Optionally combine embeddings (e.g., average)
        combined_embedding = [sum(x) / len(x) for x in zip(*embeddings)]
        return combined_embedding
    else:
        return client.get_text_embedding(text)


def clean_metadata(metadata):
    print("Cleaning metadata")
    """
    Cleans metadata to ensure it contains only valid Pinecone types:
    string, number, boolean, or list of strings.
    """
    cleaned_metadata = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)):
            cleaned_metadata[key] = value  # Keep valid types as-is
        elif isinstance(value, list):
            # Check if all elements in the list are strings
            if all(isinstance(item, str) for item in value):
                cleaned_metadata[key] = value
            else:
                print(f"Warning: Excluding invalid list metadata for key '{key}': {value}")
        else:
            print(f"Warning: Excluding invalid metadata for key '{key}': {value}")
    return cleaned_metadata


def add_documents_to_pinecone(documents):
    print("Adding documents to Pinecone")
    if not documents:
        print("Error: No documents to index.")
        return

    for i, doc in enumerate(documents):
        # Clean metadata
        metadata = clean_metadata(doc.metadata)

        # Check if the text exceeds the token limit
        if len(tokenizer.encode(doc.text)) > MAX_TOKENS:
            print(f"Document {i} exceeds token limit. Splitting into chunks.")
            chunks = chunk_text(doc.text)
            for j, chunk in enumerate(chunks):
                chunk_id = f"doc-{i}-chunk-{j}"
                embedding = client.get_text_embedding(chunk)
                pinecone_index.upsert(
                    vectors=[(chunk_id, embedding, {**metadata, "chunk_id": chunk_id})]
                )
        else:
            # Process smaller documents as usual
            embedding = client.get_text_embedding(doc.text)
            pinecone_index.upsert(
                vectors=[(f"doc-{i}", embedding, metadata)]
            )

    print(f"Indexed {len(documents)} documents (with chunks) in Pinecone.")


# Index the documents in Pinecone
add_documents_to_pinecone(documents)


def retrieve(query, k=3):
    # Generate embedding for the query
    query_embedding = client.get_text_embedding(query)

    # Query Pinecone with keyword arguments
    results = pinecone_index.query(
        vector=query_embedding,
        top_k=k,
        include_metadata=True
    )

    # Format results as a list of strings
    responses = []
    for match in results['matches']:
        metadata = match['metadata']
        score = match['score']
        response_text = f"Score: {score}\nMetadata: {metadata}"
        responses.append(response_text)

    return responses


# Example usage
query = "Find information about XYZ"
results = retrieve(query, k=3)
for res in results:
    print(res)
