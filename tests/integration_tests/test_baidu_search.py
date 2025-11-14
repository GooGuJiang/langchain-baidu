from typing import Type
from unittest.mock import patch

from langchain_tests.integration_tests import ToolsIntegrationTests

from langchain_baidu.baidu_search import BaiduSearch


class TestBaiduSearchToolIntegration(ToolsIntegrationTests):
    @property
    def tool_constructor(self) -> Type[BaiduSearch]:
        return BaiduSearch

    @property
    def tool_constructor_params(self) -> dict:
        return {
            "max_results": 5,
            "abstract_max_length": 250,
        }

    @property
    def tool_invoke_params_example(self) -> dict:
        return {"query": "北京美食", "num_results": 2}

    def test_search_invocation(self) -> None:
        tool = BaiduSearch(max_results=4)
        payload = {
            "query": "天气",
            "results": [
                {
                    "title": "天气预报",
                    "abstract": "晴朗",
                    "url": "http://example.com",
                    "rank": 1,
                }
            ],
            "response_time": 0.1,
        }
        with patch.object(tool.api_wrapper, "raw_results", return_value=payload) as mock_search:
            result = tool.invoke({"query": "天气", "num_results": 1})
        assert result == payload
        mock_search.assert_called_once_with(query="天气", num_results=1)
