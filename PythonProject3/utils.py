from __future__ import annotations


def get_existing_entries(filename: str) -> set:
    """
    Reads a news txt file and returns a set of seen URLs (lines starting with 'Link: ').
    Returns an empty set if the file does not exist.
    """
    existing_entries = set()
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith("Link: "):
                    url = line[len("Link: "):].strip()
                    if url:
                        existing_entries.add(url)
    except FileNotFoundError:
        pass
    return existing_entries


__all__ = ['get_existing_entries']

