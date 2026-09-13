from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

from taoru.rag.indexer import indexed_chunks, vector_store

bm25_retriever = BM25Retriever.from_documents(indexed_chunks)
vector_retriever = vector_store.as_retriever(search_kwargs={"k": 4})

hybrid_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.5, 0.5],
)


def retrieve(query: str):
    """Return the vault chunks most relevant to query, blending semantic and keyword search."""
    return hybrid_retriever.invoke(query)
