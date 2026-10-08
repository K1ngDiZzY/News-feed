from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

# this is where you would put your specific webhook url
get_hackerNews = os.getenv("HACKERNEWS")
get_devNews = os.getenv("DEVNEWS")
get_arcRaiderNews = os.getenv("ARCRAIDERS")
get_leagueNews = os.getenv("LEAGUENEWS")
get_apexNews = os.getenv("APEXLEGENDS")
get_deadlockNews = os.getenv("DEADLOCK")
get_wardogsNews = os.getenv("WARDOGS")

webhook = {
    'hackerNews': f"{get_hackerNews}",
    'devNews': f"{get_devNews}",
    'arcRaiderNews': f"{get_arcRaiderNews}",
    'leagueNews': f"{get_leagueNews}",
    'apexNews': f"{get_apexNews}",
    'deadlockNews': f"{get_deadlockNews}",
    'wardogsNews': f"{get_wardogsNews}"
}