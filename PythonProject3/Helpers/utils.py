from __future__ import annotations


def get_existing_entries(filename: str) -> set[str]:
    existing_entries: set[str] = set()
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith('Link: '):
                    url = line[len('Link: '):].strip()
                    if url:
                        existing_entries.add(url)
    except FileNotFoundError:
        pass
    return existing_entries


__all__ = ['get_existing_entries']
