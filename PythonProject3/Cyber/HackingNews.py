from __future__ import annotations
from datetime import datetime
import feedparser
from PythonProject3.Source.srcs import hacking_rss_list
from PythonProject3.Helpers.Discord import try_send


def get_existing_entries(filename='news.txt'):
    existing_entries = set()
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for i in range(len(lines)):
                if lines[i].startswith('Title: '):
                    title = lines[i].strip().split('Title: ')[1]
                    date = lines[i + 2].strip().split('Date: ')[1]
                    entry_date = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z').date()
                    existing_entries.add((title, entry_date))
    except FileNotFoundError:
        pass
    return existing_entries


class NewsFeed:
    def __init__(self):
        self.news = {}
        self.get_news()


    def get_news(self):
        for key, value in hacking_rss_list.items():
            feed = feedparser.parse(value)
            self.news[key] = [
                {
                    'title': entry.title,
                    'link': entry.link,
                    'date': entry.published
                }
                for entry in feed.entries
            ]

    def save_to_file(self, filename='news.txt', webhook=None):
        current_date = datetime.now().date()
        seen_entries = get_existing_entries(filename)
        sent_count = 0
        failed_count = 0

        with open(filename, 'a', encoding='utf-8') as file:  # Open in append mode
            for key, entries in self.news.items():
                file.write(f'\n\n{key}:\n')
                for entry in entries:
                    entry_date = datetime.strptime(entry['date'], '%a, %d %b %Y %H:%M:%S %z').date()
                    entry_key = (entry['title'], entry_date)  # Corrected key
                    if entry_date == current_date and entry_key not in seen_entries:
                        should_save, sent_count, failed_count = try_send(webhook, entry, sent_count, failed_count)
                        if not should_save:
                            continue

                        # Write to file only if Discord succeeded (or no webhook)
                        file.write(f'Title: {entry["title"]}\n')
                        file.write(f'Link: {entry["link"]}\n')
                        file.write(f'Date: {entry["date"]}\n')
                        file.write('\n')
                        seen_entries.add(entry_key)

        return {"sent": sent_count, "failed": failed_count}




# Clear the file
def clear_file(filename='news.txt'):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write('')