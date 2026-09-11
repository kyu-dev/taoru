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
    return vector_store.add_documents(chunk_vault())


# Runs once, at import time: the store must already hold the vault's chunks by the
# time any tool calls retrieve() on it, and there is no separate startup step.
indexed_chunks = sync_vault()

if __name__ == "__main__":
    assert len(indexed_chunks) > 0,  "expected at least one chunk to be indexed"
    print(f"Indexed {len(indexed_chunks)} chunks.")
