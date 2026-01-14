from __future__ import annotations

from webhook import webhook
from HackingNews import NewsFeed, clear_file, get_existing_entries
from Discord import SendToDiscord
from GamingNews import ArcRaidersNews, get_existing_entries as get_game_existing_entries
from datetime import datetime


def main():
    news = NewsFeed()

    # Get today's date
    today = datetime.now().date()

    print(f"Today's date: {today}")

    # Get existing entries from the news.txt file
    existing_entries = get_existing_entries()
    print(f"Existing entries: {existing_entries}")

    # Send the news to the specific discord webhook hackernews
    for key, entries in news.news.items():
        for entry in entries:
            entry_date = datetime.strptime(entry['date'], '%a, %d %b %Y %H:%M:%S %z').date()
            entry_key = (entry['title'], entry_date)
            print(f"Checking entry: {entry_key}")
            if entry_date == today and entry_key not in existing_entries:
                print(f"Sending entry to Discord: {entry_key}")
                SendToDiscord(webhook["hackerNews"], entry)
                existing_entries.add(entry_key)

    news.save_to_file()

    # --- Game news section ---
    game_news = ArcRaidersNews()
    # Fetch HTML from the Arc Raiders news page
    import requests
    try:
        response = requests.get(f"{game_news.base_url}/news")
        response.raise_for_status()
        html = response.text
        game_news.get_news(html)
    except Exception as e:
        print(f"Failed to fetch game news: {e}")

    game_existing_entries = get_game_existing_entries()
    print(f"Existing game entries: {game_existing_entries}")

    for article in game_news.news:
        try:
            article_date = datetime.strptime(article['date'], '%B %d, %Y').date()
        except Exception:
            print(f"Could not parse date for article: {article}")
            continue
        article_key = article['link']
        print(f"Checking game entry: (Title: {article['title']}, Date: {article_date}, Link: {article_key})")
        if article_date == today and article_key not in game_existing_entries:
            print(f"Sending game article to Discord: {article_key}")
            SendToDiscord(webhook["arcRaiderNews"], article)

    game_news.save_to_file()

if __name__ == "__main__":
    main()
