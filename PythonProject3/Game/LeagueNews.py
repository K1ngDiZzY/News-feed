from __future__ import annotations

from datetime import datetime

from bs4 import BeautifulSoup

from PythonProject3.Source.srcs import game_news_list
from PythonProject3.Helpers.utils import get_existing_entries
from PythonProject3.Helpers.Discord import try_send


class LeagueNews:
    def __init__(self):
        self.news = []
        self.base_url = game_news_list['leagueoflegends']
        self.feed_url = f"{self.base_url}/en-us/news/tags/patch-notes/"

    def get_news(self, html: str):
        """
        Extracts League of Legends patch note articles from HTML.
        Returns a list of dicts: { 'title': str, 'date': str, 'link': str }
        """
        soup = BeautifulSoup(html, 'html.parser')
        articles = []

        for a in soup.find_all('a', attrs={'data-testid': 'articlefeaturedcard-component'}):
            href = a.get('href', '')
            if not href:
                continue

            title_div = a.find('div', attrs={'data-testid': 'card-title'})
            time_tag = a.find('time')

            title = title_div.get_text(strip=True) if title_div else ''

            # Use ISO datetime attribute for reliable parsing
            if time_tag and time_tag.get('datetime'):
                try:
                    date_obj = datetime.fromisoformat(time_tag['datetime'].replace('Z', '+00:00')).date()
                    date = date_obj.strftime('%B %d, %Y')  # e.g. "April 28, 2026"
                except Exception:
                    date = time_tag.get_text(strip=True)
            else:
                date = ''

            link = href if href.startswith('http') else f"{self.base_url}{href}"
            articles.append({'title': title, 'date': date, 'link': link})

        self.news = articles
        return articles

    def save_to_file(self, filename='league_news.txt', webhook=None):
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
                    f.write("LeagueNews_patchnotes:\n")
                    f.write(f"Title: {title}\n")
                    f.write(f"Link: {link}\n")
                    f.write(f"Date: {date}\n\n")
                    seen_entries.add(article_key)

        return {"sent": sent_count, "failed": failed_count}


__all__ = ['LeagueNews', 'get_existing_entries']
