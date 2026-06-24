from __future__ import annotations

import re
from datetime import datetime

from bs4 import BeautifulSoup

from PythonProject3.Source.srcs import game_news_list
from PythonProject3.Helpers.utils import get_existing_entries
from PythonProject3.Helpers.Discord import try_send

_DATE_PATTERN = re.compile(
    r'\b(January|February|March|April|May|June|July|August|September|October|November|December)'
    r'\s+\d{1,2},\s+\d{4}\b'
)


class ApexNews:
    def __init__(self):
        self.news = []
        self.base_url = game_news_list['apexlegends']
        self.feed_url = f"{self.base_url}/games/apex-legends/apex-legends/news?page=1&type=latest"

    def get_news(self, html: str):
        """
        Extracts Apex Legends news articles from HTML.
        Returns a list of dicts: { 'title': str, 'date': str, 'link': str }

        The EA news page structure wraps each article in an <a> tag containing
        an <img>, a category label, a date string, and an <h3> title.
        """
        soup = BeautifulSoup(html, 'html.parser')
        articles = []

        for a in soup.find_all('a', href=True):
            href = a.get('href', '')
            # Only process links that are actual article links (not the news index page)
            if not href or '/news/' not in href:
                continue

            # Extract title from h3 element inside the anchor
            title_tag = a.find('h3')
            title = title_tag.get_text(strip=True) if title_tag else ''

            if not title:
                continue

            # Extract date by searching for a "Month DD, YYYY" pattern in all text
            full_text = a.get_text(' ')
            match = _DATE_PATTERN.search(full_text)
            if not match:
                continue
            date = match.group(0)

            link = href if href.startswith('http') else f"{self.base_url}{href}"
            articles.append({'title': title, 'date': date, 'link': link})

        self.news = articles
        return articles

    def save_to_file(self, filename='apex_news.txt', webhook=None):
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
                    title = article['title'].replace('\n', ' ')
                    link = article['link']
                    date = article['date'].replace('\n', ' ')
                    f.write("ApexNews_latest:\n")
                    f.write(f"Title: {title}\n")
                    f.write(f"Link: {link}\n")
                    f.write(f"Date: {date}\n\n")
                    seen_entries.add(article_key)

        return {"sent": sent_count, "failed": failed_count}


__all__ = ['ApexNews', 'get_existing_entries']
