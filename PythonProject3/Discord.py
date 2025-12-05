from __future__ import annotations

from typing import Dict
import logging
import requests

logger = logging.getLogger(__name__)
SESSION = requests.Session()


def send_to_discord(webhook_url: str, content: str, timeout: int = 10) -> bool:
    if not webhook_url:
        logger.warning("Empty webhook URL provided.")
        return False
    payload = {"content": content}
    headers = {"Content-Type": "application/json"}
    try:
        resp = SESSION.post(webhook_url, json=payload, headers=headers, timeout=timeout)
        if 200 <= resp.status_code < 300:
            logger.debug("Discord webhook sent (status %s).", resp.status_code)
            return True
        logger.warning("Discord webhook failed: status=%s body=%s", resp.status_code, resp.text)
        return False
    except requests.RequestException:
        logger.exception("Failed to send webhook to Discord.")
        return False


def format_entry_for_discord(entry: Dict) -> str:
    # Expect entry to have title, link and date/published
    title = entry.get('title', '').strip()
    link = entry.get('link', '').strip()
    date = entry.get('date') or entry.get('published') or ''
    return f"**{title}**\n{link}\nPublished on: {date}"
