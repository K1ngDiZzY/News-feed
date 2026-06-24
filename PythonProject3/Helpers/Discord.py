from __future__ import annotations

import requests


def send_to_discord(webhook, entry):
    content = f"**{entry['title']}**\n{entry['link']}\nPublished on: {entry['date']}"

    data = {
        "content": content
    }

    response = requests.post(webhook, json=data)
    if response.status_code != 204:
        print(f"Failed to send the message to Discord. Status code: {response.status_code}")
        return False
    else:
        print("Message sent successfully to Discord!")
        return True


def try_send(webhook, article, sent_count: int, failed_count: int) -> tuple[bool, int, int]:
    """
    Attempt to send an article to Discord.

    Returns:
        (should_save, sent_count, failed_count)
        - should_save: True if the article should be written to file, False otherwise
        - sent_count: updated sent counter
        - failed_count: updated failed counter
    """
    if not webhook:
        return True, sent_count, failed_count  # No webhook: allow saving, no send attempted

    if send_to_discord(webhook, article):
        return True, sent_count + 1, failed_count  # Success: save + increment sent
    else:
        return False, sent_count, failed_count + 1  # Failure: skip save + increment failed
