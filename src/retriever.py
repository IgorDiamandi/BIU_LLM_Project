from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
import json
import os
import boto3


embed_model = OpenAIEmbedding(embed_batch_size=42)
settings = Settings
settings.embed_model = embed_model

documents = []


#region S3
# S3 Configuration
s3_bucket_name = 'your-s3-bucket-name' #S3 Bucket name
s3_folder_path = 'data/documents/yehonatan/'  # S3 folder path
local_temp_dir = 'temp_documents/'  # Temporary local directory for processing

#Preparation for the S3 flow
s3 = boto3.client('s3')

def download_files_from_s3(bucket_name, folder_path, local_directory):
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
    if 'Contents' not in objects:
        print("No files found in S3 folder.")
        return []

    downloaded_files = []
    for obj in objects['Contents']:
        file_key = obj['Key']
        if file_key.endswith('.json'):  # Process only JSON files
            local_file_path = os.path.join(local_directory, os.path.basename(file_key))
            s3.download_file(bucket_name, file_key, local_file_path)
            downloaded_files.append(local_file_path)
    return downloaded_files

#endregion
downloaded_files = download_files_from_s3(s3_bucket_name, s3_folder_path, local_temp_dir)

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
