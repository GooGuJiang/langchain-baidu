"""Utilities for interacting with Baidu Search."""

from __future__ import annotations

import asyncio
import re
import time
import unicodedata
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

DEFAULT_HEADERS: Dict[str, str] = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
    ),
    "Referer": "https://www.baidu.com/",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

BAIDU_HOST_URL = "https://www.baidu.com"
BAIDU_SEARCH_URL = f"{BAIDU_HOST_URL}/s?ie=utf-8&tn=baidu&wd="


class BaiduSearchAPIWrapper(BaseModel):
    """Wrapper responsible for scraping search results from Baidu."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    max_results: int = Field(default=5, ge=1)
    abstract_max_length: int = Field(default=300, ge=50)
    timeout: int = Field(default=10, ge=1)
    headers: Dict[str, str] = Field(default_factory=lambda: DEFAULT_HEADERS.copy())
    baidu_host_url: str = Field(default=BAIDU_HOST_URL)
    baidu_search_url: str = Field(default=BAIDU_SEARCH_URL)

    _session: requests.Session = PrivateAttr()

    def __init__(self, **data: Any) -> None:  # pragma: no cover - delegation to BaseModel
        super().__init__(**data)
        self._session = requests.Session()
        self._session.headers.update(self.headers)

    def raw_results(self, query: str, num_results: Optional[int] = None) -> Dict[str, Any]:
        """Return cleaned Baidu search results for the provided query."""

        if not query:
            raise ValueError("Query must be a non-empty string.")

        expected_results = num_results or self.max_results
        if expected_results <= 0:
            return {"query": query, "results": [], "response_time": 0.0}

        start = time.perf_counter()
        results = self._search(query, expected_results)
        end = time.perf_counter() - start

        return {
            "query": query,
            "results": results,
            "response_time": round(end, 3),
        }

    async def raw_results_async(
        self, query: str, num_results: Optional[int] = None
    ) -> Dict[str, Any]:
        """Async version of :meth:`raw_results`."""

        return await asyncio.to_thread(self.raw_results, query, num_results)

    def clean_text(self, value: Optional[str]) -> str:
        """Clean text fields by removing control chars and collapsing whitespace."""

        if not value:
            return ""

        without_controls = "".join(
            ch for ch in value if unicodedata.category(ch)[0] != "C"
        )
        without_newlines = without_controls.replace("\r", " ").replace("\n", " ")
        compacted = re.sub(r"\s+", " ", without_newlines)
        return compacted.strip()

    def _search(self, keyword: str, num_results: int) -> List[Dict[str, Any]]:
        """Iterate through Baidu result pages until enough results are collected."""

        results: List[Dict[str, Any]] = []
        page_url = self._build_search_url(keyword)
        rank_start = 0

        while len(results) < num_results and page_url:
            page_results, next_url = self._parse_html(page_url, rank_start)
            results.extend(page_results)
            rank_start = len(results)
            page_url = next_url

        return results[:num_results]

    def _build_search_url(self, keyword: str) -> str:
        encoded = quote_plus(keyword)
        return f"{self.baidu_search_url}{encoded}"

    def _parse_html(
        self, url: str, rank_start: int
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        response = self._session.get(url, timeout=self.timeout)
        response.raise_for_status()
        response.encoding = "utf-8"
        root = BeautifulSoup(response.text, "html.parser")

        content_left = root.find("div", id="content_left")
        if content_left is None:
            return [], None

        parsed: List[Dict[str, Any]] = []
        for div in content_left.contents:
            if not isinstance(div, Tag):
                continue

            class_list = div.get("class", [])
            if not class_list or "c-container" not in class_list:
                continue

            title_tag = div.find("h3")
            link_tag = title_tag.find("a") if title_tag else None
            title = self.clean_text(title_tag.get_text(" ")) if title_tag else ""
            url_value = (
                link_tag.get("href", "") if link_tag is not None else ""
            )

            abstract_tag = div.find("div", class_="c-abstract") or div.find("div")
            abstract = (
                self.clean_text(abstract_tag.get_text(" ")) if abstract_tag else ""
            )

            if len(abstract) > self.abstract_max_length:
                abstract = abstract[: self.abstract_max_length].rstrip() + "…"

            parsed.append(
                {
                    "title": title,
                    "abstract": abstract,
                    "url": self._normalize_url(url_value),
                    "rank": rank_start + len(parsed) + 1,
                }
            )

        next_link = root.find_all("a", class_="n")
        next_url = None
        if next_link:
            candidate = next_link[-1]
            if "下一页" in candidate.get_text(" "):
                next_url = self._normalize_url(candidate.get("href", ""))

        return parsed, next_url

    def _normalize_url(self, url: str) -> str:
        if not url:
            return ""
        if url.startswith("http"):
            return url
        if url.startswith("//"):
            return f"https:{url}"
        if url.startswith("/"):
            return f"{self.baidu_host_url.rstrip('/')}{url}"
        return url

