"""
vector_store.py  -  ChromaDB wrapper.

ChromaDB turns text into embeddings (numbers that capture meaning) using a
built-in model (all-MiniLM-L6-v2) and lets us search by meaning, not keywords.
The model downloads automatically the first time (~80 MB).
"""
import chromadb

_client = chromadb.PersistentClient(path="data/chroma")
collection = _client.get_or_create_collection(name="documents")


def add_chunks(file_name, chunks):
    # Remove old version of this file so re-ingesting doesn't create duplicates
    collection.delete(where={"file_name": file_name})
    collection.add(
        ids=[f"{file_name}::{i}" for i in range(len(chunks))],
        documents=chunks,
        metadatas=[{"file_name": file_name, "chunk_index": i} for i in range(len(chunks))],
    )


def search(question, k=3):
    """Return the k chunks most similar in meaning to the question."""
    if collection.count() == 0:
        return []
    k = min(k, collection.count())
    result = collection.query(query_texts=[question], n_results=k)
    docs = result["documents"][0]
    metas = result["metadatas"][0]
    return [{"text": d, "file_name": m["file_name"], "chunk_index": m["chunk_index"]}
            for d, m in zip(docs, metas)]
