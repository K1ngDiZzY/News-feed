from webhook import webhook
from HackingNews import NewsFeed as HackNewsFeed, get_existing_entries
from GamingNews import NewsFeed as GameNewsFeed, get_existing_game_entries
from Discord import SendToDiscord
from datetime import datetime


def main():
    # Hacking/news feeds
    news = HackNewsFeed()

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

    # Arc Raiders (gaming) news using simplified NewsFeed
    gnews = GameNewsFeed()
    existing_game_entries = get_existing_game_entries()
    for entry in gnews.news.get('arcraiders', []):
        try:
            entry_date = datetime.fromisoformat(entry['date']).date()
        except Exception:
            continue
        entry_key = (entry['title'], entry['link'])
        print(f"Checking game entry: {entry_key}")
        if entry_date == today and entry_key not in existing_game_entries:
            print(f"Sending game entry to Discord: {entry_key}")
            SendToDiscord(webhook['arcraiders'],
                          {'title': entry['title'], 'link': entry['link'], 'date': entry['date']})
            existing_game_entries.add(entry_key)

    gnews.save_to_file()


if __name__ == "__main__":
    main()
