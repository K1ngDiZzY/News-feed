from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup

from PythonProject3.Helpers.Discord import try_send
from PythonProject3.Helpers.utils import get_existing_entries
from PythonProject3.Source.srcs import game_news_list


class WardogsNews:
    def __init__(self):
        self.news = []
        self.base_url = game_news_list['wardogs']
        self.feed_url = self.base_url

    def _extract_rss_items(self, xml_text: str):
        try:
            root = ET.fromstring(xml_text)
            items = []
            for item in root.findall('.//item'):
                title = (item.findtext('title') or '').strip()
                link = (item.findtext('link') or item.findtext('guid') or '').strip()
                raw_date = (item.findtext('pubDate') or item.findtext('pubdate') or '').strip()
                items.append((title, link, raw_date))
            return items
        except ET.ParseError:
            return None

    def _extract_html_items(self, xml_text: str):
        soup = BeautifulSoup(xml_text, 'html.parser')
        items = []
        for item in soup.find_all('item'):
            # pyrefly: ignore [missing-attribute]
            title = (item.find('title').get_text(' ', strip=True) if item.find('title') else '').strip()
            link = ''
            link_tag = item.find('link')
            if link_tag is not None:
                link = (link_tag.get_text(' ', strip=True) or '').strip()
                if not link:
                    match = re.search(r'<link[^>]*>(.*?)</link>', str(item), flags=re.I | re.S)
                    if match:
                        link = html.unescape(match.group(1)).strip()
            if not link:
                guid_tag = item.find('guid')
                if guid_tag is not None:
                    link = (guid_tag.get_text(' ', strip=True) or '').strip()
            raw_date = ''
            pub_tag = item.find('pubDate') or item.find('pubdate')
            if pub_tag is not None:
                raw_date = pub_tag.get_text(' ', strip=True)
            items.append((title, link, raw_date))
        return items

    def get_news(self, xml: str):
        """
        Extracts WARDOGS items from the Steam RSS feed.
        Returns a list of dicts: { 'title': str, 'date': str, 'link': str }
        """
        items = self._extract_rss_items(xml)
        if items is None:
            items = self._extract_html_items(xml)

        articles = []
        for title, link, raw_date in items:
            if not title or not link:
                continue
            try:
                date = parsedate_to_datetime(raw_date).strftime('%B %d, %Y') if raw_date else ''
            except Exception:
                date = raw_date
            articles.append({'title': title, 'date': date, 'link': link})

        self.news = articles
        return articles

    def save_to_file(self, filename='wardogs_news.txt', webhook=None):
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

                    title = str(article.get('title', '')).replace('\n', ' ')
                    link = str(article.get('link', ''))
                    date = str(article.get('date', '')).replace('\n', ' ')
                    f.write("WardogsNews_steam:\n")
                    f.write(f"Title: {title}\n")
                    f.write(f"Link: {link}\n")
                    f.write(f"Date: {date}\n\n")
                    seen_entries.add(article_key)

        return {"sent": sent_count, "failed": failed_count}


__all__ = ['WardogsNews']