from webhook import webhook
from HackingNews import NewsFeed, clear_file, get_existing_entries
from Discord import SendToDiscord
import schedule
import time
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

if __name__ == "__main__":
    main()