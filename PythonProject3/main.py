from __future__ import annotations

import requests

from PythonProject3.Game.WardogsNews import WardogsNews
from PythonProject3.Source.webhook import webhook


def _safe_send(label: str, webhook_url: str | None, operation):
    try:
        result = operation(webhook=webhook_url)
    except Exception as exc:
        print(f"{label}: Failed to send news: {exc}")
        return {"sent": 0, "failed": 1}

    print(f"{label}: Sent {result['sent']}, Failed: {result['failed']}")
    return result


def main():
    # news = NewsFeed()
    #
    # today = datetime.now().date()
    # print(f"Today's date: {today}")
    #
    # result = _safe_send("HackerNews", webhook.get("hackerNews"), news.save_to_file)
    #
    # game_news = ArcRaidersNews()
    # try:
    #     response = requests.get(f"{game_news.base_url}/news", timeout=15)
    #     response.raise_for_status()
    #     game_news.get_news(response.text)
    # except Exception as exc:
    #     print(f"Failed to fetch game news: {exc}")
    #
    # _safe_send("ArcRaiders", webhook.get("arcRaiderNews"), game_news.save_to_file)
    #
    # league_news = LeagueNews()
    # try:
    #     response = requests.get(league_news.feed_url, timeout=15)
    #     response.raise_for_status()
    #     league_news.get_news(response.text)
    # except Exception as exc:
    #     print(f"Failed to fetch League news: {exc}")
    #
    # _safe_send("League", webhook.get("leagueNews"), league_news.save_to_file)
    #
    # apex_news = ApexNews()
    # try:
    #     response = requests.get(apex_news.feed_url, timeout=15)
    #     response.raise_for_status()
    #     apex_news.get_news(response.text)
    # except Exception as exc:
    #     print(f"Failed to fetch Apex Legends news: {exc}")
    #
    # _safe_send("Apex", webhook.get("apexNews"), apex_news.save_to_file)
    #
    # deadlock_news = DeadlockNews()
    # try:
    #     response = requests.get(deadlock_news.base_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
    #     response.raise_for_status()
    #     deadlock_news.get_news(response.text)
    # except Exception as exc:
    #     print(f"Failed to fetch Deadlock news: {exc}")
    #
    # _safe_send("Deadlock", webhook.get("deadlockNews"), deadlock_news.save_to_file)

    wardogs_news = WardogsNews()
    try:
        response = requests.get(wardogs_news.feed_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        wardogs_news.get_news(response.text)
    except Exception as exc:
        print(f"Failed to fetch WARDOGS news: {exc}")

    _safe_send("WARDOGS", webhook.get("wardogsNews"), wardogs_news.save_to_file)


if __name__ == "__main__":
    main()