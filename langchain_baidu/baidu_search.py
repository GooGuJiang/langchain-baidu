"""Baidu Search tool for LangChain."""

from __future__ import annotations

from typing import Any, Dict, Optional, Type

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, ConfigDict, Field

from langchain_baidu._utilities import BaiduSearchAPIWrapper, DEFAULT_HEADERS


class BaiduSearchInput(BaseModel):
    """Input schema for the :class:`BaiduSearch` tool."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(..., description="A natural language query to send to Baidu search")
    num_results: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
        description=(
            "Maximum number of search results to return for this invocation. "
            "When omitted the tool level `max_results` is used."
        ),
    )


class BaiduSearch(BaseTool):  # type: ignore[misc]
    """LangChain tool that performs a Baidu search and returns cleaned results."""

    name: str = "baidu_search"
    description: str = (
        "Use Baidu to search Chinese-language web content. "
        "Useful for discovering up-to-date information and references in the Chinese web."
    )
    args_schema: Type[BaseModel] = BaiduSearchInput
    handle_tool_error: bool = True

    max_results: int = Field(default=5, ge=1, description="Default maximum number of results")
    abstract_max_length: int = Field(
        default=300, ge=50, description="Maximum characters to keep per result abstract"
    )
    timeout: int = Field(default=10, ge=1, description="HTTP timeout when querying Baidu")
    headers: Dict[str, str] = Field(
        default_factory=lambda: DEFAULT_HEADERS.copy(),
        description="HTTP headers attached to Baidu requests",
    )
    api_wrapper: BaiduSearchAPIWrapper = Field(default_factory=BaiduSearchAPIWrapper)

    def __init__(self, **kwargs: Any) -> None:
        wrapper_provided = "api_wrapper" in kwargs
        super().__init__(**kwargs)
        if not wrapper_provided:
            self.api_wrapper = BaiduSearchAPIWrapper(
                max_results=self.max_results,
                abstract_max_length=self.abstract_max_length,
                timeout=self.timeout,
                headers=self.headers.copy(),
            )

    def _run(
        self,
        query: str,
        num_results: Optional[int] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **_: Any,
    ) -> Dict[str, Any]:
        desired_results = num_results or self.max_results
        try:
            payload = self.api_wrapper.raw_results(query=query, num_results=desired_results)
            if not payload.get("results"):
                raise ToolException(
                    "Baidu did not return any results. Try another query or adjust filters."
                )
            return payload
        except ToolException:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            raise ToolException(str(exc))

    async def _arun(
        self,
        query: str,
        num_results: Optional[int] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
        **_: Any,
    ) -> Dict[str, Any]:
        desired_results = num_results or self.max_results
        try:
            payload = await self.api_wrapper.raw_results_async(
                query=query, num_results=desired_results
            )
            if not payload.get("results"):
                raise ToolException(
                    "Baidu did not return any results. Try another query or adjust filters."
                )
            return payload
        except ToolException:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            raise ToolException(str(exc))

