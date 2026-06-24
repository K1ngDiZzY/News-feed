from __future__ import annotations

from datetime import datetime

import requests

from PythonProject3.Game.ApexNews import ApexNews
from PythonProject3.Game.DeadlockNews import DeadlockNews
from PythonProject3.Game.GamingNews import ArcRaidersNews
from PythonProject3.Game.LeagueNews import LeagueNews
from PythonProject3.Cyber.HackingNews import NewsFeed
from PythonProject3.Source.webhook import webhook


def main():
    news = NewsFeed()

    # Get today's date
    today = datetime.now().date()

    print(f"Today's date: {today}")

    # Send the news to the specific discord webhook hackernews
    result = news.save_to_file(webhook=webhook["hackerNews"])
    print(f"HackerNews: Sent {result['sent']}, Failed: {result['failed']}")

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

    result = game_news.save_to_file(webhook=webhook["arcRaiderNews"])
    print(f"ArcRaiders: Sent {result['sent']}, Failed: {result['failed']}")

    # --- League of Legends patch notes section ---
    league_news = LeagueNews()
    try:
        response = requests.get(league_news.feed_url)
        response.raise_for_status()
        league_news.get_news(response.text)
    except Exception as e:
        print(f"Failed to fetch League news: {e}")

    result = league_news.save_to_file(webhook=webhook["leagueNews"])
    print(f"League: Sent {result['sent']}, Failed: {result['failed']}")

    # --- Apex Legends news section ---
    apex_news = ApexNews()
    try:
        response = requests.get(apex_news.feed_url)
        response.raise_for_status()
        apex_news.get_news(response.text)
    except Exception as e:
        print(f"Failed to fetch Apex Legends news: {e}")

    result = apex_news.save_to_file(webhook=webhook["apexNews"])
    print(f"Apex: Sent {result['sent']}, Failed: {result['failed']}")

    # --- Deadlock news section ---
    deadlock_news = DeadlockNews()
    try:
        response = requests.get(deadlock_news.base_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        deadlock_news.get_news(response.text)
    except Exception as e:
        print(f"Failed to fetch Deadlock news: {e}")

    result = deadlock_news.save_to_file(webhook=webhook["deadlockNews"])
    print(f"Deadlock: Sent {result['sent']}, Failed: {result['failed']}")


if __name__ == "__main__":
    main()
