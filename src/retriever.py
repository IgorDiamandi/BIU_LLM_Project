from pinecone import Pinecone
from llama_index.embeddings.openai import OpenAIEmbedding
from config.config_helper import pinecone_api_key, openai_api_key

# Initialize Pinecone and OpenAI clients
pc = Pinecone(api_key=pinecone_api_key)
client = OpenAIEmbedding(openai_api_key=openai_api_key)

# Function to retrieve documents from Pinecone
def retrieve(query, pinecone_index_name="biullmindex", k=3):
    pinecone_index = pc.Index(pinecone_index_name)
    print(f"\n pinecone_index: {pinecone_index}")

    query_embedding = client.get_text_embedding(query)
    print(f"\n query_embedding: {query_embedding}")

    results = pinecone_index.query(
        vector=query_embedding,
        top_k=k,
        include_metadata=True
    )
    responses = []
    for match in results['matches']:
        metadata = match['metadata']
        score = match['score']
        response_text = f"Score: {score}\nMetadata: {metadata}"
        responses.append(response_text)
    return responses
