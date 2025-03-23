from dotenv import load_dotenv
import os

load_dotenv()

# this is where you would put your specific webhook url
get_hackerNews = os.getenv("HACKERNEWS")
get_devNews = os.getenv("DEVNEWS")

webhook = {
        'hackerNews': f"{get_hackerNews}",
        'devNews': f"{get_devNews}"
    }