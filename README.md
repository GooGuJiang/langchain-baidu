# 🦜️🔗 LangChain Baidu Search

**LangChain Baidu Search** 是一个适用于 LangChain 的百度搜索工具，通过抓取百度搜索结果页面，提供结构化的搜索结果输出。
适用于需要中文搜索能力的智能体（Agent）、问答系统或自动化流程。

本项目中与百度搜索结果获取相关的部分实现，参考并复用自项目：[`amazingcoderpro/python-baidusearch`](https://github.com/amazingcoderpro/python-baidusearch)。

⚠ **重要说明**
本项目通过模拟浏览器行为抓取百度页面，属于爬虫方式。
请避免高频或批量调用，以免触发反爬或造成不必要的负载。
如需稳定、高并发或商业使用，请申请百度官方提供的接口服务。

---

## 📦 安装

该项目暂未发布至 PyPI，请通过 GitHub 安装。

### 使用 pip 安装

```bash
pip install git+https://github.com/GooGuJiang/langchain-baidu.git
```

### 在 Poetry 项目中安装

```bash
poetry add git+https://github.com/GooGuJiang/langchain-baidu.git
```

### 可选：指定分支、标签或提交

```bash
pip install git+https://github.com/GooGuJiang/langchain-baidu.git@main
```

---

## 🔑 认证信息

百度搜索抓取无需 API Key。
库中默认设置了合理的请求头、超时与行为模拟，你也可以在构造实例时进行自定义。

---

## 🔍 Baidu Search 工具使用

`BaiduSearch` 的使用方式与 LangChain 中的其他工具保持一致。
可以配置默认参数，例如：

* `max_results`：默认返回的搜索条数
* `abstract_max_length`：摘要最大长度
* `timeout`：请求超时时间（秒）

示例：

```python
from langchain_baidu import BaiduSearch

search_tool = BaiduSearch(
    max_results=5,
    abstract_max_length=300,
    timeout=10,
)
```

---

### ▶ 直接调用

```python
search_tool.invoke({"query": "圆头耄耋是什么意思", "num_results": 3})
```

返回示例：

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

---

## 🤖 与 LangChain Agent 配合使用

你可以将 `BaiduSearch` 工具绑定到基于 OpenAI 的 Agent 模型中，让智能体自动决定何时触发搜索指令：

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
    ("system", "你是一个使用百度搜索回答问题的智能助手"),
    MessagesPlaceholder(variable_name="messages"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_openai_tools_agent(
    llm=llm,
    tools=[baidu_search_tool],
    prompt=prompt,
)

executor = AgentExecutor(
    agent=agent,
    tools=[baidu_search_tool],
    verbose=True
)

response = executor.invoke(
    {"messages": [{"role": "user", "content": "最新的上海天气"}]}
)
```

---

## ⚠ 注意事项

* 本项目基于爬虫方式模拟访问百度页面并解析搜索结果。
* 百度可能会针对异常流量、频繁请求或未经授权的抓取行为进行限制。
* **请勿将本工具用于高频、批量、商业或自动化大规模抓取场景。**
* 如需可靠的大规模搜索能力，请使用百度官方搜索 API。

---

## 🙏 致谢

本项目中与百度搜索结果获取相关的逻辑，部分参考并复用自：

* [`amazingcoderpro/python-baidusearch`](https://github://github.com/amazingcoderpro/python-baidusearch)

感谢原项目作者的工作和开源贡献。