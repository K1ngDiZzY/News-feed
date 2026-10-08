from __future__ import annotations

import re
from datetime import datetime
from email.utils import parsedate_to_datetime

import requests
from bs4 import BeautifulSoup

from PythonProject3.Helpers.Discord import try_send
from PythonProject3.Helpers.utils import get_existing_entries
from PythonProject3.Source.srcs import game_news_list

_DATE_FORMATS = [
    '%B %d, %Y',  # June 10, 2025
    '%b %d, %Y',  # Jun 10, 2025
    '%d %B, %Y',  # 10 June, 2025
    '%d %b, %Y',  # 10 Jun, 2025
]

_DATE_PATTERN = re.compile(
    r'\b(?:'
    r'(?:January|February|March|April|May|June|July|August|September|October|November|December'
    r'|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
    r'\s+\d{1,2},\s+\d{4}'
    r'|\d{1,2}\s+'
    r'(?:January|February|March|April|May|June|July|August|September|October|November|December'
    r'|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
    r',\s+\d{4})\b'
)


def _parse_date(raw: str) -> str:
    """
    Normalize a raw Steam date string to 'Month DD, YYYY' format.
    Returns an empty string if parsing fails.
    """
    raw = ' '.join(raw.split())  # collapse extra whitespace
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).strftime('%B %d, %Y')
        except ValueError:
            continue
    # Fall back to regex extraction
    match = _DATE_PATTERN.search(raw)
    if match:
        snippet = match.group(0)
        for fmt in _DATE_FORMATS:
            try:
                return datetime.strptime(snippet, fmt).strftime('%B %d, %Y')
            except ValueError:
                continue
    return raw


class DeadlockNews:
    def __init__(self):
        self.news = []
        self.base_url = game_news_list['deadlock']

    def get_news(self, html: str):
        """
        Extracts Deadlock news articles from the Steam app news page HTML.
        Returns a list of dicts: { 'title': str, 'date': str, 'link': str }

        Steam news pages wrap each article inside a
        ``<div class="apphub_PostSummaryFull">`` block.  Within that block:
        - The article link is carried by an ``<a>`` tag whose class contains
          ``apphub_CardContentPreviewImageLink``.
        - The title lives in ``<div class="apphub_CardContentTitle">``.
        - The publication date lives in ``<div class="apphub_PostSummaryDate">``.
        """
        soup = BeautifulSoup(html, 'html.parser')
        articles = []

        for container in soup.find_all('div', class_='apphub_PostSummaryFull'):
            link_tag = container.find('a', class_='apphub_CardContentPreviewImageLink') or container.find('a',
                                                                                                          href=True)
            # pyrefly: ignore [missing-attribute]
            href = link_tag.get('href', '').strip() if link_tag else ''
            # Normalize href to string types in case of unexpected attribute values
            if href is None:
                href = ''
            if isinstance(href, bytes):
                try:
                    href = href.decode('utf-8')
                except Exception:
                    href = href.decode('utf-8', 'ignore')
            if not isinstance(href, str):
                try:
                    iterable = list(href)
                    href = str(iterable[0]) if iterable else str(href)
                except Exception:
                    href = str(href)

            title_div = container.find('div', class_='apphub_CardContentTitle')
            date_div = container.find('div', class_='apphub_PostSummaryDate')

            title = title_div.get_text(strip=True) if title_div else ''
            raw_date = date_div.get_text(strip=True) if date_div else ''
            date = _parse_date(raw_date)

            if not title or not href:
                continue

            link = href if href.startswith('http') else f"{self.base_url}{href}"
            articles.append({'title': title, 'date': date, 'link': link})

        # If the HTML page appears empty (Steam renders news with JS), fall back to the Steam RSS feed
        if not articles:
            try:
                feed_url = self.base_url.replace('/news/app/', '/feeds/news/app/')
                resp = requests.get(feed_url, timeout=20)
                resp.raise_for_status()
                # Prefer XML parser when available; fall back to HTML parser and suppress XML-as-HTML warning
                try:
                    from bs4 import FeatureNotFound
                    feed_soup = BeautifulSoup(resp.text, features='xml')
                except Exception:
                    import warnings
                    from bs4 import XMLParsedAsHTMLWarning
                    with warnings.catch_warnings():
                        warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)
                        feed_soup = BeautifulSoup(resp.text, 'html.parser')
                items = feed_soup.find_all('item')
                for it in items:
                    # pyrefly: ignore [missing-attribute]
                    title = it.find('title').text.strip() if it.find('title') else ''
                    pub = it.find('pubDate') or it.find('pubdate')
                    date = ''
                    if pub and pub.text:
                        try:
                            date_obj = parsedate_to_datetime(pub.text.strip())
                            date = date_obj.strftime('%B %d, %Y')
                        except Exception:
                            date = pub.text.strip()
                    link = ''
                    link_tag = it.find('link')
                    guid_tag = it.find('guid')
                    if link_tag and link_tag.text:
                        link = link_tag.text.strip()
                    elif guid_tag and guid_tag.text:
                        link = guid_tag.text.strip()
                    else:
                        link = self.base_url

                    if title and link:
                        articles.append({'title': title, 'date': date, 'link': link})
            except Exception:
                # If feed fetch fails, leave articles empty
                pass

        self.news = articles
        return articles

    def save_to_file(self, filename='deadlock_news.txt', webhook=None):
        current_date = datetime.now().date()
        seen_entries = get_existing_entries(filename)
        sent_count = 0
        failed_count = 0

        with open(filename, 'a', encoding='utf-8') as f:
            for article in self.news:
                try:
                    article_date = datetime.strptime(article['date'], '%B %d, %Y').date()
                except Exception:
                    continue
                article_key = article['link']
                if article_date == current_date and article_key not in seen_entries:
                    should_save, sent_count, failed_count = try_send(webhook, article, sent_count, failed_count)
                    if not should_save:
                        continue

                    # Write to file only if Discord succeeded (or no webhook)
                    title = str(article.get('title', '')).replace('\n', ' ')
                    link = str(article.get('link', ''))
                    date = str(article.get('date', '')).replace('\n', ' ')
                    f.write("DeadlockNews:\n")
                    f.write(f"Title: {title}\n")
                    f.write(f"Link: {link}\n")
                    f.write(f"Date: {date}\n\n")
                    seen_entries.add(article_key)

        return {"sent": sent_count, "failed": failed_count}


__all__ = ['DeadlockNews', 'get_existing_entries']