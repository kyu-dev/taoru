from langchain.tools import tool

from taoru.infrastructure.obsidian import (
    create_note,
    edit_note,
    resolve_in_vault,
    delete_note,
)


@tool
def read_obsidian_note(path: str) -> str:
    """Read the full markdown content of one note in the user's Obsidian vault.

    Args:
        path: Vault-relative path to the note, as returned by search_obsidian_note.
    """
    with open(resolve_in_vault(path), encoding="utf-8") as f:
        return f.read()

@tool
def edit_obsidian_note(path: str, old_content: str, new_content: str,
                       replace_all: bool = False) -> str:
    """Edit an existing note of the user's Obsidian vault.

    Replaces old_content with new_content. old_content must match exactly once, so
    read the note first and include enough surrounding lines to make the passage
    unique. Leave old_content empty to append new_content at the end of the note
    instead, and leave new_content empty to delete the passage.

    To insert a passage between two existing ones, anchor on the one that follows:
    set old_content to it, and new_content to the text to insert followed by that
    same anchor. There is no separate insert operation.

    Args:
        path: Vault-relative path to the note, as returned by search_obsidian_note.
        old_content: Exact text to replace, whitespace included. Empty means append.
        new_content: Text to write in its place. Empty means delete.
        replace_all: Replace every occurrence at once. Only set this when the intent is
            really to change all of them; to fix a single ambiguous passage, quote more
            surrounding text instead.
    """
    found = edit_note(path, old_content, new_content, replace_all)

    if found == 0:
        return f"No change: old_content not found in {path}. Read the note and copy the passage verbatim."
    if found > 1 and not replace_all:
        return f"No change: old_content matches {found} times in {path}. Quote more surrounding lines to make it unique, or set replace_all to change them all."

    return f"Edited {path} ({found} occurrence(s) replaced)."

@tool
def create_obsidian_note(path: str, content: str) -> str:
    """Create a brand new note in the user's Obsidian vault.

    Never overwrites: if a note already sits at that path, nothing is written and
    edit_obsidian_note should be used instead. Missing folders are created, and a
    ".md" extension is added when the path has none.

    Args:
        path: Vault-relative path for the new note, folders included.
        content: Full markdown body of the note.
    """
    created = create_note(path, content)
    return f"Created {created}." if created else f"No change: {path} already exists."

@tool
def delete_obsidian_note(path: str) -> str:
    """Move a note of the user's Obsidian vault to its .trash folder.

    Nothing is erased for good, so the user can still restore the note from Obsidian.

    Args:
        path: Vault-relative path to the note, as returned by search_obsidian_note.
    """
    trashed = delete_note(path)
    return f"Moved {path} to {trashed}." if trashed else f"No change: {path} not found."

TOOLS = [
    read_obsidian_note,
    edit_obsidian_note,
    create_obsidian_note,
    delete_obsidian_note,
]
