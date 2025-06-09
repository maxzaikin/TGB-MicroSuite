"""
generate_tree.py

📂 A universal directory tree generator with exclusion rules.

This script recursively prints a tree representation of a given directory,
excluding specific files, file extensions, and directory names (e.g., virtual environments,
IDE folders, caches, and hidden system folders).

Exclusions:
- Hidden directories and files starting with '.'
- Common development folders like `.git`, `__pycache__`, `venv`, `node_modules`, etc.
- Files with extensions like `.pyc`, `.log`, `.jpg`, `.svg`, etc.

Usage:
    $ python generate_tree.py ./your_project

Example output:
    your_project/
    ├── main.py
    ├── src
    │   └── utils.py
    └── README.md
"""
from pathlib import Path

# Exclusion rules
EXCLUDED_FILE_EXTENSIONS = {
    '.pyc',
    '.log',
    '.jpg',
    '.svg',
}
EXCLUDED_DIR_NAMES = {
    '.git',
    '.idea',
    '__pycache__',
    '.vscode',
    'venv',
    '.mypy_cache',
    'node_modules',
    'versions',
    'dist',
}
EXCLUDED_FILE_NAMES = set()

# Tree drawing characters
INDENT = "│   "
BRANCH = "├── "
LAST_BRANCH = "└── "

def is_excluded(path: Path) -> bool:
    """
    Determine whether a file or directory should be excluded from the tree output.

    Args:
        path (Path): The file or directory path to check.

    Returns:
        bool: True if the path matches any exclusion rule, otherwise False.
    """
    if path.name in EXCLUDED_FILE_NAMES:
        return True
    if path.suffix in EXCLUDED_FILE_EXTENSIONS:
        return True
    if path.is_dir() and (path.name in EXCLUDED_DIR_NAMES or path.name.startswith(".")):
        return True
    return False

def tree(directory: Path, prefix: str = "") -> list[str]:
    """
    Recursively build the tree structure as a list of strings.

    Args:
        directory (Path): The root directory to scan.
        prefix (str): The string prefix used for formatting the tree branches.

    Returns:
        list[str]: A list of formatted strings representing the directory tree.
    """
    entries = [
        entry for entry in sorted(directory.iterdir(), 
                                  key=lambda e: (not e.is_dir(), 
                                                 e.name.lower()))
        if not is_excluded(entry)
    ]

    lines = []
    for idx, entry in enumerate(entries):
        connector = LAST_BRANCH if idx == len(entries) - 1 else BRANCH
        line = f"{prefix}{connector}{entry.name}"
        lines.append(line)

        if entry.is_dir():
            extension = "    " if idx == len(entries) - 1 else INDENT
            lines.extend(tree(entry, prefix + extension))
    return lines

def generate_tree(root_path: str) -> None:
    """
    Generate and print a formatted directory tree from the given root path.

    Args:
        root_path (str): The root directory path to start scanning.

    Example:
        >>> generate_tree("./my_project")
        my_project/
        ├── main.py
        ├── src
        │   └── utils.py
        └── README.md
    """
    path = Path(root_path).resolve()
    if not path.exists() or not path.is_dir():
        print(f"❌ Path '{path}' does not exist or is not a directory.")
        return

    print(f"{path.name}/")
    tree_lines = tree(path)
    for line in tree_lines:
        print(line)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="📂 Universal folder tree generator with exclusion rules.")
    parser.add_argument("path", type=str, help="Path to the root folder (e.g. ./TGramBuddy)")
    args = parser.parse_args()

    generate_tree(args.path)
