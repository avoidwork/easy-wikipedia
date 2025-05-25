"""
title: Easy Wikipedia
author: Jason Mulligan <jason.mulligan@avoidwork.com>
author_url: https://github.com/avoidwork
funding_url: https://github.com/avoidwork/easy-wikipedia
version: 1.0.4
"""

import requests
import json
import re
from html.parser import HTMLParser
from urllib.parse import quote

BASE_URL = "https://en.wikipedia.org/api/rest_v1"
LANGUAGE = "en-US"


class EasyWikipediaHTMLParser(HTMLParser):
    _tags = ["h1", "h2", "h3", "h4", "p"]
    _text = []
    _stream = []
    _capture = False

    def handle_starttag(self, tag, _args):
        if tag in self._tags:
            self._capture = True
            self._stream.clear()

    def handle_endtag(self, tag):
        if tag in self._tags:
            self._capture = False
            text = "".join(self._stream)
            text = text.strip().rstrip()
            text = re.sub(r"\[[^\]]+\]", "", text)
            if len(text) > 1:
                trailing_char = "\n" if tag == "p" else ""
                formatted_text = f"{text}{trailing_char}"
                self._text.append(formatted_text)
            self._stream.clear()

    def handle_data(self, data):
        if self._capture:
            invalid = len(data.strip()) > 1 and all(
                word.startswith(".") for word in data.split(" ")
            )
            if not invalid:
                self._stream.append(data)

    def close(self):
        text = "\n".join(self._text)
        self._text.clear()
        return text


def parse_html(page_html):
    parser = EasyWikipediaHTMLParser()
    parser.feed(page_html)
    return parser.close()


class Tools:
    def __init__(self) -> None:
        self.citation = True
        pass

    def page(self, title: str) -> str:
        """
        Retrieves a Wikipedia page and parses it.
        :param title: The title of the page.
        :return: Text of the page.
        """
        search_title = title.strip().strip('"').strip("'")
        url = f"{BASE_URL}/page/html/{quote(search_title)}?redirect=false&stash=false"
        headers = {
            "Accept": 'text/html; charset=utf-8; profile="https://www.mediawiki.org/wiki/Specs/HTML/2.1.0"',
            "Accept-Language": LANGUAGE,
        }
        resp = requests.get(url, headers=headers)
        data = resp.text
        if len(data) == 0:
            return f'Failed to fetch page for "{search_title}".'
        return parse_html(data)

    def search(self, title: str) -> str:
        """
        Retrieves a Wikipedia page summary.
        :param title: The title of the page.
        :return: Summary of the page.
        """
        search_title = title.strip().strip('"').strip("'")
        url = f"{BASE_URL}/page/summary/{quote(search_title)}?redirect=false"
        headers = {"Accept": "application/json", "Accept-Language": LANGUAGE}
        resp = requests.get(url, headers=headers)
        data = resp.json()
        if not isinstance(data, dict):
            return f'Failed to fetch page summary for "{search_title}".'
        page = {
            "title": data.get("title"),
            "description": data.get("description"),
            "url": data.get("content_urls", {}).get("desktop", {}).get("page"),
            "timestamp": data.get("timestamp"),
            "revision": data.get("revision"),
        }
        return json.dumps(page)
