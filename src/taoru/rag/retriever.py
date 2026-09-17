from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

# Module import: reindex_note reassigns indexer.indexed_chunks, which only a module
# reference (not a name imported by value) picks up.
import taoru.rag.indexer as indexer
import taoru.rag.ingest as ingest

bm25_retriever = BM25Retriever.from_documents(indexer.indexed_chunks)
vector_retriever = indexer.vector_store.as_retriever(search_kwargs={"k": 4})

hybrid_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.5, 0.5],
)


def retrieve(query: str):
    """Return the vault chunks most relevant to query, blending semantic and keyword search."""
    return hybrid_retriever.invoke(query)


def reindex_note(path: str):
    """Bring the index up to date with the current on-disk state of one note.

    vector_retriever isn't rebuilt (reads vector_store live); bm25_retriever has no
    incremental API, so it and hybrid_retriever are rebuilt from indexer.indexed_chunks.
    """
    global bm25_retriever, hybrid_retriever

    old_ids = [
        id for id, doc in indexer.vector_store.store.items()
        if doc["metadata"]["source"] == path
    ]
    indexer.vector_store.delete(ids=old_ids)

    indexer.indexed_chunks = [c for c in indexer.indexed_chunks if c.metadata["source"] != path]

    new_chunks = ingest.chunk_note(path)
    if new_chunks:
        new_ids = [f"{c.metadata['source']}#{c.metadata['start_index']}" for c in new_chunks]
        indexer.vector_store.add_documents(new_chunks, ids=new_ids)
        indexer.indexed_chunks += new_chunks

    bm25_retriever = BM25Retriever.from_documents(indexer.indexed_chunks)
    hybrid_retriever = EnsembleRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        weights=[0.5, 0.5],
    )
