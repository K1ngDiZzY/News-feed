from discord_webhook import DiscordWebhook
import requests
import json

def SendToDiscord(webhook, entry):
    content = f"**{entry['title']}**\n{entry['link']}\nPublished on: {entry['date']}"

    data = {
        "content": content
    }

    response = requests.post(webhook, json=data)
    if response.status_code != 204:
        print(f"Failed to send the message to Discord. Status code: {response.status_code}")
    else:
        print("Message sent successfully to Discord!")
