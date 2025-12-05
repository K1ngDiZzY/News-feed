from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, datetime, timezone
from typing import Dict, List, Optional, Set, Tuple
import json
import logging
import time

import feedparser
from dateutil import parser as dateparser  # add python-dateutil to requirements

from srcs import hacking_rss_list

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HackEntry:
    title: str
    link: str
    published: date

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['published'] = self.published.isoformat()
        return d


def _to_date(published_str: Optional[str], published_parsed) -> Optional[date]:
    # published_parsed: struct_time when available
    if published_parsed:
        try:
            ts = time.mktime(published_parsed)
            return datetime.fromtimestamp(ts, tz=timezone.utc).date()
        except Exception:
            pass
    if published_str:
        try:
            dt = dateparser.parse(published_str, fuzzy=True)
            if dt:
                return dt.date()
        except Exception:
            pass
    return None


def load_seen(filename: str = 'hacking_seen.json') -> Set[Tuple[str, str]]:
    try:
        with open(filename, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        return {(item['title'], item['published']) for item in data}
    except FileNotFoundError:
        return set()
    except Exception:
        logger.exception("Failed to load hacking seen file; starting fresh.")
        return set()


def save_seen(seen: Set[Tuple[str, str]], filename: str = 'hacking_seen.json') -> None:
    payload = [{'title': t, 'published': p} for t, p in sorted(seen)]
    try:
        with open(filename, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
    except Exception:
        logger.exception("Failed to write hacking seen file.")


class NewsFeed:
    def __init__(self):
        self.news: Dict[str, List[HackEntry]] = {}

    def fetch(self) -> None:
        for key, url in hacking_rss_list.items():
            try:
                feed = feedparser.parse(url)
            except Exception:
                logger.exception("Failed to parse feed %s", url)
                self.news[key] = []
                continue

            items: List[HackEntry] = []
            for entry in getattr(feed, 'entries', []):
                title = getattr(entry, 'title', '') or ''
                link = getattr(entry, 'link', '') or ''
                published_str = getattr(entry, 'published', None) or getattr(entry, 'updated', None)
                published_parsed = getattr(entry, 'published_parsed', None) or getattr(entry, 'updated_parsed', None)

                pdate = _to_date(published_str, published_parsed)
                if pdate:
                    items.append(HackEntry(title=title.strip(), link=link.strip(), published=pdate))
            # sort newest first
            items.sort(key=lambda e: e.published, reverse=True)
            self.news[key] = items

    def new_entries_since_today(self, seen_file: str = 'hacking_seen.json') -> Dict[str, List[HackEntry]]:
        seen = load_seen(seen_file)
        today = date.today()
        out: Dict[str, List[HackEntry]] = {}
        for key, items in self.news.items():
            new = [i for i in items if (i.title, i.published.isoformat()) not in seen and i.published == today]
            out[key] = new
        return out

    def mark_as_seen(self, entries: Dict[str, List[HackEntry]], seen_file: str = 'hacking_seen.json') -> None:
        seen = load_seen(seen_file)
        for key, items in entries.items():
            for i in items:
                seen.add((i.title, i.published.isoformat()))
        save_seen(seen, seen_file)
