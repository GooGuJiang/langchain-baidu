from typing import Type
from unittest.mock import AsyncMock, patch

import pytest
from langchain_core.tools import ToolException
from langchain_tests.unit_tests import ToolsUnitTests

from langchain_baidu.baidu_search import BaiduSearch


class TestBaiduSearchToolUnit(ToolsUnitTests):
    @pytest.fixture(autouse=True)
    def setup_mocks(self, request: pytest.FixtureRequest) -> None:
        sample_payload = {
            "query": "test",
            "results": [
                {"title": "Example", "abstract": "Snippet", "url": "http://example.com", "rank": 1}
            ],
            "response_time": 0.01,
        }

        def fake_raw_results(self, *_, **__):
            return getattr(self, "_test_payload", sample_payload)

        async def fake_raw_results_async(self, *_, **__):
            return getattr(self, "_test_payload", sample_payload)

        sync_patcher = patch(
            "langchain_baidu.baidu_search.BaiduSearchAPIWrapper.raw_results",
            new=fake_raw_results,
        )
        async_patcher = patch(
            "langchain_baidu.baidu_search.BaiduSearchAPIWrapper.raw_results_async",
            new=fake_raw_results_async,
        )
        sync_patcher.start()
        async_patcher.start()
        request.addfinalizer(sync_patcher.stop)
        request.addfinalizer(async_patcher.stop)

    @property
    def tool_constructor(self) -> Type[BaiduSearch]:
        return BaiduSearch

    @property
    def tool_constructor_params(self) -> dict:
        return {
            "max_results": 5,
            "abstract_max_length": 200,
            "timeout": 5,
        }

    @property
    def tool_invoke_params_example(self) -> dict:
        return {"query": "圆头耄耋", "num_results": 3}

    def test_tool_raises_when_no_results(self) -> None:
        tool = BaiduSearch()
        tool.api_wrapper._test_payload = {"query": "foo", "results": []}
        assert tool.api_wrapper.raw_results("foo")["results"] == []
        result = tool.invoke({"query": "foo"})
        assert isinstance(result, str)
        assert "Baidu did not return any results" in result
