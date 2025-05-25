"""
title: Easy Wikipedia
author: Jason Mulligan <jason.mulligan@avoidwork.com>
author_url: https://github.com/avoidwork
funding_url: https://github.com/avoidwork/easy-wikipedia
version: 1.0.0
"""

import requests
import json
from urllib.parse import quote

BASE_URL = "https://en.wikipedia.org/api/rest_v1"
LANGUAGE = "en-US"


class Tools:
    def __init__(self) -> None:
        self.citation = True
        pass

    def summary(self, title: str) -> str:
        search_title = title.strip().strip('"').strip("'")
        url = f"{BASE_URL}/page/summary/{quote(search_title)}?redirect=false"
        headers = {"Accept": "application/json", "Accept-Language": LANGUAGE}
        resp = requests.get(url, headers=headers)
        data = resp.json()
        if not isinstance(data, dict):
            return f"Failed to fetch page summary for {search_title}."
        page = {
            "title": data.get("title"),
            "description": data.get("description"),
            "url": data.get("content_urls", {}).get("desktop", {}).get("page"),
            "timestamp": data.get("timestamp"),
            "revision": data.get("revision"),
        }
        result = f"""Show the page summary result:

{json.dumps(page)}
"""
        return result
