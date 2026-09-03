from langchain_text_splitters import RecursiveCharacterTextSplitter

from taoru.infrastructure.obsidian import iter_notes

# Markdown headings first: a chunk that breaks on "\n## " stays one section of a note,
# so the embedding sees a whole idea instead of half of two.
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    add_start_index=True,
)


def chunk_vault():
    """Cut every note of the vault into Documents carrying their source path.

    The vault-relative path travels in each chunk's metadata, so a retrieved chunk can
    still say which note it came from — and the other Obsidian tools can reopen it.
    """
    notes = iter_notes()
    return splitter.create_documents(
        texts=[content for _, content in notes],
        metadatas=[{"source": path} for path, _ in notes],
    )

