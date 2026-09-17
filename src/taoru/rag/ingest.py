from langchain_text_splitters import RecursiveCharacterTextSplitter

from taoru.infrastructure.obsidian import iter_notes, resolve_in_vault

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


def chunk_note(path):
    """Cut one note into Documents, or [] if it no longer exists on disk.

    The single-note counterpart to chunk_vault(), for reindexing one note after an
    edit without re-chunking the whole vault.
    """
    full = resolve_in_vault(path)
    if not full.is_file():
        return []

    return splitter.create_documents(
        texts=[full.read_text(encoding="utf-8")],
        metadatas=[{"source": path}],
    )

