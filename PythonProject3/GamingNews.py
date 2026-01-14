from __future__ import annotations

from datetime import datetime
from srcs import game_news_list
from bs4 import BeautifulSoup

def get_existing_entries(filename='arc_raiders_news.txt'):
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



class ArcRaidersNews:
    def __init__(self):
        self.news = []
        self.base_url = game_news_list['arcraiders']

    def get_news(self, html: str):
        """
        Extracts game news articles from HTML using BeautifulSoup.
        Returns a list of dicts: { 'href': str, 'title': str, 'date': str, 'link': str }
        """
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        for a in soup.find_all('a', class_='news-article-card_container__xsniv'):
            href = a.get('href', '')
            if not href.startswith('/news/'):
                continue
            title_div = a.find('div', class_='news-article-card_title__7LpPs')
            date_div = a.find('div', class_='news-article-card_date__fJqI_')
            title = title_div.get_text(strip=True) if title_div else ''
            date = date_div.get_text(strip=True) if date_div else ''
            # Build full link
            link = href if href.startswith('http') else f"{self.base_url}{href}"
            articles.append({'href': href, 'title': title, 'date': date, 'link': link})
        self.news = articles
        return articles

    def save_to_file(self, filename='arc_raiders_news.txt'):
        from datetime import datetime
        current_date = datetime.now().date()
        seen_entries = get_existing_entries(filename)
        with open(filename, 'a', encoding='utf-8') as f:  # Append mode
            for article in self.news:
                # Parse date and only save today's entries
                try:
                    article_date = datetime.strptime(article['date'], '%B %d, %Y').date()
                except Exception:
                    continue
                article_key = article['link']
                if article_date == current_date and article_key not in seen_entries:
                    title = article['title'].replace('\n', ' ')
                    link = article['link']
                    date = article['date'].replace('\n', ' ')
                    f.write("ArcRaidersNews_home:\n")
                    f.write(f"Title: {title}\n")
                    f.write(f"Link: {link}\n")
                    f.write(f"Date: {date}\n\n")


__all__ = ['ArcRaidersNews', 'get_existing_entries']
