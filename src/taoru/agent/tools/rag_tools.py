from langchain.tools import tool

from taoru.rag.retriever import retrieve


@tool
def search_obsidian_vault(query: str) -> str:
    """Search the user's Obsidian vault for notes relevant to a query.

    Use this to ground answers in the user's own notes instead of guessing.

    Args:
        query: What to look for, phrased as a question or topic.
    """
    docs = retrieve(query)
    if not docs:
        return "No relevant notes found."
    return "\n\n".join(f"Source: {doc.metadata['source']}\n{doc.page_content}" for doc in docs)


TOOLS = [search_obsidian_vault]
