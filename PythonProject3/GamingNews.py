from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Dict, List, Optional, Set, Tuple
import json
import logging
import re

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser  # add python-dateutil to requirements
from urllib.parse import urljoin

from srcs import game_news_list

logger = logging.getLogger(__name__)
SESSION = requests.Session()


@dataclass(frozen=True)
class GameEntry:
    title: str
    link: str
    date: date

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['date'] = self.date.isoformat()
        return d


def _parse_date_string(date_text: Optional[str]) -> Optional[date]:
    if not date_text:
        return None
    s = date_text.strip()
    # Try dateutil first (covers most formats)
    try:
        dt = dateparser.parse(s, fuzzy=True)
        if dt:
            return dt.date()
    except Exception:
        pass
    # Fallback: extract YYYY-MM-DD
    m = re.search(r'(\d{4}-\d{2}-\d{2})', s)
    if m:
        try:
            return datetime.strptime(m.group(1), '%Y-%m-%d').date()
        except Exception:
            pass
    return None


def _sanitize_text(html: str) -> str:
    return BeautifulSoup(html or '', 'html.parser').get_text(separator=' ', strip=True)


def load_seen(filename: str = 'gamenews_seen.json') -> Set[Tuple[str, str]]:
    try:
        with open(filename, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        return {(item['title'], item['link']) for item in data}
    except FileNotFoundError:
        return set()
    except Exception:
        logger.exception("Failed to load seen game entries, starting empty.")
        return set()


def save_seen(seen: Set[Tuple[str, str]], filename: str = 'gamenews_seen.json') -> None:
    payload = [{'title': t, 'link': l} for t, l in sorted(seen)]
    try:
        with open(filename, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
    except Exception:
        logger.exception("Failed to save seen game entries.")


class NewsFeed:
    def __init__(self, source_key: str = 'arcraiders'):
        self.source_key = source_key
        self.url = game_news_list.get(source_key)
        self.news: List[GameEntry] = []

    def fetch(self, timeout: int = 15) -> None:
        self.news = []
        if not self.url:
            logger.warning("No URL configured for %s", self.source_key)
            return

        try:
            resp = SESSION.get(self.url, timeout=timeout)
            resp.raise_for_status()
        except Exception:
            logger.exception("Failed to fetch %s", self.url)
            return

        soup = BeautifulSoup(resp.text, 'html.parser')
        # Try structured news cards first
        cards = soup.select('a[class*="news-article-card_container"]') or []
        if not cards:
            # Generic fallback: top anchors under main/content
            main = soup.find('main') or soup.find(id='content') or soup
            cards = main.find_all('a')[:50]

        entries: List[GameEntry] = []
        for card in cards:
            try:
                # Structured card path
                title_el = card.select_one('[class*="news-article-card_title"]')
                date_el = card.select_one('[class*="news-article-card_date"]')
                if title_el and date_el and card.get('href'):
                    title = _sanitize_text(title_el.get_text())
                    link = card.get('href')
                    if link.startswith('/'):
                        link = urljoin(self.url, link)
                    parsed = _parse_date_string(date_el.get_text())
                    if parsed:
                        entries.append(GameEntry(title=title, link=link, date=parsed))
                    continue
            except Exception:
                logger.debug("Structured card parse failed for one card.", exc_info=True)

            # Generic anchor path
            try:
                a = card if card.name == 'a' else card.find('a')
                if not a or not a.get('href'):
                    continue
                title = _sanitize_text(a.get_text() or a.get('title') or '')
                link = a.get('href')
                if link.startswith('/'):
                    link = urljoin(self.url, link)
                # Look for nearby time tags or date-like nodes
                date_text = None
                time_tag = card.find('time') if hasattr(card, 'find') else None
                if time_tag:
                    date_text = time_tag.get('datetime') or time_tag.get_text()
                else:
                    p = card.select_one('[class*=date]') or card.find('span', string=re.compile(r'\d{4}'))
                    if p:
                        date_text = p.get_text()
                parsed = _parse_date_string(date_text) if date_text else None
                if parsed:
                    entries.append(GameEntry(title=title, link=link, date=parsed))
            except Exception:
                logger.debug("Generic card parse failed for one card.", exc_info=True)

        # Deduplicate by (title, link), prefer newest date
        seen_keys: Dict[Tuple[str, str], GameEntry] = {}
        for e in entries:
            key = (e.title, e.link)
            existing = seen_keys.get(key)
            if not existing or e.date > existing.date:
                seen_keys[key] = e

        # Sort by date desc
        self.news = sorted(seen_keys.values(), key=lambda e: e.date, reverse=True)

    def new_entries_since_today(self, seen_file: str = 'gamenews_seen.json') -> List[GameEntry]:
        seen = load_seen(seen_file)
        today = date.today()
        new = [e for e in self.news if (e.title, e.link) not in seen and e.date == today]
        return new

    def mark_as_seen(self, entries: List[GameEntry], seen_file: str = 'gamenews_seen.json') -> None:
        seen = load_seen(seen_file)
        for e in entries:
            seen.add((e.title, e.link))
        save_seen(seen, seen_file)
