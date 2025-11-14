from typing import Type

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
