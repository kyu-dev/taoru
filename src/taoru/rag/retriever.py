from taoru.rag.store import vector_store


def retrieve(query: str, k: int = 4):
    """Return the k vault chunks most relevant to query, ranked by similarity."""
    return vector_store.similarity_search(query, k=k)
