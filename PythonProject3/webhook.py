from __future__ import annotations

from typing import Dict
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)
load_dotenv()


def get_webhooks() -> Dict[str, str]:
    # Explicit keys, avoid f-strings for env mapping noise
    webhooks = {
        'hackerNews': os.getenv('HACKERNEWS', '').strip(),
        'devNews': os.getenv('DEVNEWS', '').strip(),
        'arcraiders': os.getenv('ARCRAIDERS', '').strip(),
    }
    missing = [k for k, v in webhooks.items() if not v]
    if missing:
        logger.debug("Missing webhook values for: %s", missing)
    return webhooks
