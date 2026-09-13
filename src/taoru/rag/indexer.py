from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings

from taoru.rag.ingest import chunk_vault

embeddings = OllamaEmbeddings(model="qwen3-embedding")
vector_store = InMemoryVectorStore(embedding=embeddings)


def sync_vault():
    """(Re)index the whole vault into the in-memory store.

    No persistence between runs: the store is rebuilt from scratch every launch,
    so there's nothing to keep in sync incrementally.
    """
    chunks = chunk_vault()
    vector_store.add_documents(chunks)
    return chunks


# Runs once, at import time: the vector store must hold the vault's chunks, and
# indexed_chunks must be available, before retriever.py builds its retrievers from
# them — there is no separate startup step.
indexed_chunks = sync_vault()

if __name__ == "__main__":
    assert len(indexed_chunks) > 0, "expected at least one chunk to be indexed"
    print(f"Indexed {len(indexed_chunks)} chunks.")
