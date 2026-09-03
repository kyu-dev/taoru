import glob
from pathlib import Path

from taoru.config import settings

VAULT = settings.obsidian_vault.resolve()

def iter_notes(vault=VAULT):
    """Read every note of the vault as (vault-relative path, content) pairs.

    The path is the one the other tools speak, so a caller can hand it straight to
    resolve_in_vault or read the note again later. A note that disappears mid-walk is
    skipped instead of fatal: the vault sits on iCloud, where a file can be evicted
    between the listing and the read.
    """
    notes = []

    for relative in glob.glob("**/*.md", root_dir=vault, recursive=True):
        try:
            with open(Path(vault) / relative, encoding="utf-8", errors="ignore") as f:
                notes.append((relative, f.read()))
        except FileNotFoundError:
            continue

    return notes


def resolve_in_vault(path, vault=VAULT):
    """Turn a model-supplied note path into an absolute path inside the vault.

    Raises ValueError for anything escaping it (../, absolute paths, symlinks out).
    """
    
    vault = Path(vault).resolve()
    full = (vault / path).resolve()
    if not full.is_relative_to(vault):
        raise ValueError(f"Path outside the Obsidian vault: {path}")
    return full

def search_lines(keywords, limit=20, vault=VAULT):
    """Find the lines of the vault's notes containing any keyword, case-insensitively.

    Returns "<vault-relative path>:<line number>:<text>" strings, at most 3 per note
    so a single verbose note cannot fill the whole result.
    """
    needles = [word.lower() for word in keywords]
    results = []

    # glob's "*" never matches a leading dot, so .obsidian/.trash/.git are already out
    for relative in glob.glob("**/*.md", root_dir=vault, recursive=True):
        found_here = 0

        # errors="ignore": one badly encoded note must not kill the whole search
        with open(Path(vault) / relative, encoding="utf-8", errors="ignore") as f:
            for number, line in enumerate(f, 1):
                if not any(needle in line.lower() for needle in needles):
                    continue

                results.append(f"{relative}:{number}:{line.strip()[:200]}")
                found_here += 1

                if found_here >= 3 or len(results) >= limit:
                    break

        if len(results) >= limit:
            break

    return results

def edit_note(path, old_string, new_string, replace_all=False, vault=VAULT):
    """Replace old_string in a note, or append new_string when old_string is empty.

    Returns how many times old_string was found. Nothing is written when that is zero,
    or more than one without replace_all — the caller decides what to say about it.
    An appended passage is separated from the existing body by a newline when needed.
    """
    full = resolve_in_vault(path, vault)
    content = full.read_text(encoding="utf-8")

    if not old_string:
        separator = "\n" if content and not content.endswith("\n") else ""
        full.write_text(content + separator + new_string, encoding="utf-8")
        return 1

    found = content.count(old_string)
    if found == 0 or (found > 1 and not replace_all):
        return found

    full.write_text(
        content.replace(old_string, new_string, -1 if replace_all else 1),
        encoding="utf-8",
    )
    return found

def trash_note(path, vault=VAULT):
    """Move a note to the vault's .trash folder instead of deleting it.

    Returns the vault-relative path it now sits at, or None if the note did not
    exist. Never overwrites an already-trashed note of the same name: a counter is
    appended instead, so nothing in the trash is ever lost either.
    """
    vault = Path(vault).resolve()
    full = resolve_in_vault(path, vault)
    if not full.is_file():
        return None

    trash = vault / ".trash"
    trash.mkdir(exist_ok=True)

    target = trash / full.name
    collisions = 1
    while target.exists():
        target = trash / f"{full.stem} {collisions}{full.suffix}"
        collisions += 1

    full.replace(target)
    return str(target.relative_to(vault))

def create_note(path, content, vault=VAULT):
    """Write a brand new note in the vault, never touching an existing one.

    Missing parent folders are created, and a ".md" extension is added when the path
    has none, so the note actually shows up in Obsidian. Returns the vault-relative
    path of the new note, or None if something already sits there.
    """
    if not Path(path).suffix:
        path += ".md"

    vault = Path(vault).resolve()
    full = resolve_in_vault(path, vault)
    full.parent.mkdir(parents=True, exist_ok=True)

    try:
        # mode "x": never overwrite, and no read-then-write race to get wrong
        with open(full, "x", encoding="utf-8") as f:
            f.write(content)
    except FileExistsError:
        return None

    return str(full.relative_to(vault))
