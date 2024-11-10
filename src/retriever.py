from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from .document_store import DocumentStore

model = SentenceTransformer('all-MiniLM-L6-v2')
document_store = DocumentStore()

if document_store.documents:
    document_embeddings = model.encode(document_store.documents)
    dimension = document_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(document_embeddings))
else:
    print("Error: No documents to create embeddings. Please add documents to the 'data/documents/' directory.")
    document_embeddings = None
    index = None


def retrieve(query, k=3):
    if document_embeddings is None:
        return ["No documents available to retrieve information from."]

    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding), k)
    return [document_store.documents[i] for i in indices[0]]
