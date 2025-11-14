"""LangChain Baidu integration."""

from importlib import metadata
from typing import List

from langchain_baidu.baidu_search import BaiduSearch

try:
    __version__: str = metadata.version(__package__)
except metadata.PackageNotFoundError:  # pragma: no cover - package metadata missing
    __version__ = ""

del metadata

__all__: List[str] = ["BaiduSearch", "__version__"]
