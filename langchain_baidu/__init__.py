from importlib import metadata
from typing import List

from langchain_tavily.tavily_search import TavilySearch

try:
    __version__: str = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)

__all__: List[str] = [
    "TavilySearch",
    "__version__",
]
