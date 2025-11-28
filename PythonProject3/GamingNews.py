from bs4 import BeautifulSoup
import requests
from datetime import datetime
from srcs import game_news_list
from urllib.parse import urljoin
import re


def _parse_date_string(date_text):
    if not date_text:
        return None
    s = date_text.strip()
    # common format like 'November 13, 2025'
    try:
        return datetime.strptime(s, '%B %d, %Y').date()
    except Exception:
        pass
    # try abbreviated month 'Nov 13, 2025'
    try:
        return datetime.strptime(s, '%b %d, %Y').date()
    except Exception:
        pass
    # try ISO
    try:
        return datetime.fromisoformat(s).date()
    except Exception:
        pass
    # try to extract yyyy-mm-dd
    m = re.search(r'(\d{4}-\d{2}-\d{2})', s)
    if m:
        try:
            return datetime.strptime(m.group(1), '%Y-%m-%d').date()
        except Exception:
            pass
    return None


def get_existing_game_entries(filename='gamenews.txt'):
    existing_entries = set()
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for i in range(len(lines)):
                if lines[i].startswith('Title: '):
                    title = lines[i].strip().split('Title: ')[1]
                    if i + 2 < len(lines) and lines[i + 2].startswith('Date: '):
                        date_str = lines[i + 2].strip().split('Date: ')[1]
                        try:
                            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        except Exception:
                            try:
                                entry_date = datetime.fromisoformat(date_str).date()
                            except Exception:
                                entry_date = None
                        existing_entries.add((title, entry_date))
    except FileNotFoundError:
        pass
    return existing_entries


class NewsFeed:
    def __init__(self):
        self.news = {}
        self.get_news()

    def get_news(self):
        url = game_news_list.get('arcraiders')
        entries = []
        if not url:
            self.news['arcraiders'] = entries
            return
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f'Failed to fetch Arc Raiders news page: {e}')
            self.news['arcraiders'] = entries
            return

        soup = BeautifulSoup(resp.text, 'html.parser')
        cards = soup.select('a[class*="news-article-card_container"]')
        if not cards:
            # fallback: look for anchor list
            main = soup.find('main') or soup.find(id='content') or soup
            cards = main.find_all('a')[:30]

        for card in cards:
            try:
                # if it's a card with structured fields
                title_el = card.select_one('[class*="news-article-card_title"]')
                date_el = card.select_one('[class*="news-article-card_date"]')
                if title_el and date_el and card.get('href'):
                    title = title_el.get_text().strip()
                    link = card.get('href')
                    if link.startswith('/'):
                        link = urljoin(url, link)
                    date_obj = _parse_date_string(date_el.get_text())
                    if not date_obj:
                        # skip if date not parseable
                        continue
                    entries.append({'title': title, 'link': link, 'date': date_obj.isoformat()})
                    continue
            except Exception:
                pass

            # generic fallback for anchors
            try:
                a = card if card.name == 'a' else card.find('a')
                if not a or not a.get('href'):
                    continue
                title = (a.get_text() or a.get('title') or '').strip()
                link = a.get('href')
                if link.startswith('/'):
                    link = urljoin(url, link)
                # try to find nearby date text
                date_text = None
                time_tag = card.find('time') if hasattr(card, 'find') else None
                if time_tag:
                    date_text = time_tag.get('datetime') or time_tag.get_text()
                else:
                    # look for child with 'date' in class
                    p = card.select_one('[class*=date]')
                    if p:
                        date_text = p.get_text()
                date_obj = _parse_date_string(date_text) if date_text else None
                if not date_obj:
                    continue
                entries.append({'title': title, 'link': link, 'date': date_obj.isoformat()})
            except Exception:
                continue

        # deduplicate by (title,link)
        seen = set()
        unique = []
        for e in entries:
            key = (e['title'], e['link'])
            if key in seen:
                continue
            seen.add(key)
            unique.append(e)

        # sort by date desc
        unique.sort(key=lambda x: x['date'], reverse=True)
        self.news['arcraiders'] = unique

    def save_to_file(self, filename='gamenews.txt'):
        seen_entries = get_existing_game_entries(filename)
        with open(filename, 'a', encoding='utf-8') as file:
            file.write('\n\narcraiders:\n')
            for entry in self.news.get('arcraiders', []):
                try:
                    entry_date = datetime.fromisoformat(entry['date']).date()
                except Exception:
                    continue
                entry_key = (entry['title'], entry['link'])
                if entry_key not in seen_entries:
                    file.write(f"Title: {entry['title']}\n")
                    file.write(f"Link: {entry['link']}\n")
                    file.write(f"Date: {entry['date']}\n")
                    file.write('\n')
                    seen_entries.add(entry_key)


# Clear the file
def clear_file(filename='gamenews.txt'):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write('')
