from dotenv import load_dotenv
import os

load_dotenv()

# this is where you would put your specific webhook url
get_hackerNews = os.getenv("HACKERNEWS")
get_devNews = os.getenv("DEVNEWS")
get_arcraiders = os.getenv("ARCRAIDERS")

webhook = {
    'hackerNews': f"{get_hackerNews}",
    'devNews': f"{get_devNews}",
    'arcraiders': f"{get_arcraiders}"
}
