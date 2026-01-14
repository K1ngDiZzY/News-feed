from __future__ import annotations

from dotenv import load_dotenv
import os

load_dotenv()

# this is where you would put your specific webhook url
get_hackerNews = os.getenv("HACKERNEWS")
get_devNews = os.getenv("DEVNEWS")
get_arcRaiderNews = os.getenv("ARCRAIDERNEWS")

webhook = {
        'hackerNews': f"{get_hackerNews}",
        'devNews': f"{get_devNews}",
        'arcRaiderNews': f"{get_arcRaiderNews}"
    }