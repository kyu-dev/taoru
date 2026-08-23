import os


def find_obsidian_vault(path):
    for root, dirs, _ in os.walk(path):
        if ".obsidian" in dirs:
            return root

    raise FileNotFoundError("No Obsidian vault found")

vault = find_obsidian_vault(os.path.expanduser("~"))

def find_md(vault):
    for root, _ , files in os.walk(vault):
        for file in files:
            if file.endswith(".md"):
                yield os.path.join(root, file)


