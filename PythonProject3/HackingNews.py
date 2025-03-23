import feedparser
from srcs import hacking_rss_list

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

    def print_news(self):
        for key, entries in self.news.items():
            print(f'\n\n{key}:\n')
            for i, entry in enumerate(entries[:5]):
                print(f'{i+1}. {entry["title"]} - {entry["link"]} (Published on: {entry["date"]})')