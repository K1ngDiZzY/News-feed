from __future__ import annotations
from datetime import datetime
import requests
from video_games.ApexNews import ApexNews, get_existing_entries as get_apex_existing_entries
from Discord import SendToDiscord
from video_games.GamingNews import ArcRaidersNews, get_existing_entries as get_game_existing_entries
from news.HackingNews import NewsFeed, get_existing_entries
from video_games.LeagueNews import LeagueNews, get_existing_entries as get_league_existing_entries
from webhook import webhook


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
    try:
        response = requests.get(f"{game_news.base_url}/news")
        response.raise_for_status()
        html = response.text
        game_news.get_news(html)
    except Exception as e:
        print(f"Failed to fetch game news: {e}")

    game_existing_entries = get_game_existing_entries('arc_raiders_news.txt')
    print(f"Existing game entries: {game_existing_entries}")

    for article in game_news.news:
        try:
            article_date = datetime.strptime(article['date'], '%B %d, %Y').date()
        except Exception as e:
            print(f"Could not parse date for article: {e}")
            continue
        article_key = article['link']
        print(f"Checking game entry: (Title: {article['title']}, Date: {article_date}, Link: {article_key})")
        if article_date == today and article_key not in game_existing_entries:
            print(f"Sending game article to Discord: {article_key}")
            SendToDiscord(webhook["arcRaiderNews"], article)

    game_news.save_to_file()

    # --- League of Legends patch notes section ---
    league_news = LeagueNews()
    try:
        response = requests.get(league_news.feed_url)
        response.raise_for_status()
        league_news.get_news(response.text)
    except Exception as e:
        print(f"Failed to fetch League news: {e}")

    league_existing_entries = get_league_existing_entries('league_news.txt')
    print(f"Existing League entries: {league_existing_entries}")

    for article in league_news.news:
        try:
            article_date = datetime.strptime(article['date'], '%B %d, %Y').date()
        except Exception as e:
            print(f"Could not parse date for article: {e}")
            continue
        article_key = article['link']
        print(f"Checking League entry: (Title: {article['title']}, Date: {article_date}, Link: {article_key})")
        if article_date == today and article_key not in league_existing_entries:
            print(f"Sending League article to Discord: {article_key}")
            SendToDiscord(webhook["leagueNews"], article)

    league_news.save_to_file()

    # --- Apex Legends news section ---
    apex_news = ApexNews()
    try:
        response = requests.get(apex_news.feed_url)
        response.raise_for_status()
        apex_news.get_news(response.text)
    except Exception as e:
        print(f"Failed to fetch Apex Legends news: {e}")

    apex_existing_entries = get_apex_existing_entries('apex_news.txt')
    print(f"Existing Apex entries: {apex_existing_entries}")

    for article in apex_news.news:
        try:
            article_date = datetime.strptime(article['date'], '%B %d, %Y').date()
        except Exception as e:
            print(f"Invalid or missing date format for Apex article: {e}")
            continue
        article_key = article['link']
        print(f"Checking Apex entry: (Title: {article['title']}, Date: {article_date}, Link: {article_key})")
        if article_date == today and article_key not in apex_existing_entries:
            print(f"Sending Apex article to Discord: {article_key}")
            SendToDiscord(webhook["apexNews"], article)

    apex_news.save_to_file()


if __name__ == "__main__":
    main()
