# 🦜️🔗 LangChain Baidu Search

This package exposes a LangChain compatible tool that performs web searches by
scraping Baidu result pages. It is designed for use in agents or workflows that
need Chinese-language search capabilities without depending on the Tavily API.

```bash
pip install -U langchain-baidu
```

---

## Installation

```bash
pip install -U langchain-baidu
```

### Credentials

Baidu search scraping does not require an API key. The tool ships with sensible
HTTP headers and timeouts but you can customise them during instantiation.

## Baidu Search Tool

The `BaiduSearch` tool mirrors the ergonomics of other LangChain tools. It can
be configured with default values such as `max_results`, `abstract_max_length`
or `timeout`, and individual invocations can override the number of requested
results.

```python
from langchain_baidu import BaiduSearch

search_tool = BaiduSearch(
    max_results=5,
    abstract_max_length=300,
    timeout=10,
)
```

### Invoke directly with args

```python
search_tool.invoke({"query": "圆头耄耋是什么意思", "num_results": 3})
```

Example output:

```json
{
  "query": "圆头耄耋是什么意思",
  "results": [
    {
      "title": "圆头耄耋(网络用语) - 百度百科",
      "abstract": "含义：形容头部圆润且脾气差的小猫。",
      "url": "http://www.baidu.com/link?...",
      "rank": 1
    }
  ],
  "response_time": 0.41
}
```

### Agent Tool Calling

You can bind the tool to an OpenAI compatible agent. The agent can dynamically
set invocation level arguments (`query`, `num_results`) while the defaults set
at construction time remain in effect.

```python
from typing import Any, Dict

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_baidu import BaiduSearch

llm = init_chat_model(model="gpt-4o", model_provider="openai", temperature=0)
baidu_search_tool = BaiduSearch(max_results=5)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful assistant that answers questions using Baidu search",
    ),
    MessagesPlaceholder(variable_name="messages"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_openai_tools_agent(
    llm=llm,
    tools=[baidu_search_tool],
    prompt=prompt,
)

agent_executor = AgentExecutor(agent=agent, tools=[baidu_search_tool], verbose=True)
response = agent_executor.invoke({"messages": [{"role": "user", "content": "最新的上海天气"}]})
```

