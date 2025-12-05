from __future__ import annotations

import logging
from datetime import date
from typing import Dict

from webhook import get_webhooks
from HackingNews import NewsFeed as HackNewsFeed
from GamingNews import NewsFeed as GameNewsFeed
from Discord import send_to_discord, format_entry_for_discord

# Configure basic logging. Replace or extend with your preferred config.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    webhooks: Dict[str, str] = get_webhooks()
    today = date.today()
    logger.info("Running news sync for date: %s", today.isoformat())

    # Hacking/news feeds
    hack_feed = HackNewsFeed()
    hack_feed.fetch()
    new_hacking = hack_feed.new_entries_since_today()
    for source, entries in new_hacking.items():
        wh = webhooks.get('hackerNews')  # per-source customization can be added
        for e in entries:
            payload = {'title': e.title, 'link': e.link, 'published': e.published.isoformat()}
            content = format_entry_for_discord(payload)
            if send_to_discord(wh, content):
                logger.info("Sent hack entry: %s", e.title)
            else:
                logger.warning("Failed to send hack entry: %s", e.title)
    hack_feed.mark_as_seen(new_hacking)

    # Gaming feed (Arc Raiders)
    game_feed = GameNewsFeed(source_key='arcraiders')
    game_feed.fetch()
    new_games = game_feed.new_entries_since_today()
    wh_game = webhooks.get('arcraiders')
    for e in new_games:
        payload = {'title': e.title, 'link': e.link, 'date': e.date.isoformat()}
        content = format_entry_for_discord(payload)
        if send_to_discord(wh_game, content):
            logger.info("Sent game entry: %s", e.title)
        else:
            logger.warning("Failed to send game entry: %s", e.title)
    game_feed.mark_as_seen(new_games)

    logger.info("Run complete.")


if __name__ == "__main__":
    main()
