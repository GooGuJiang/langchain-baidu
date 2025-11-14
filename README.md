# 🦜️🔗 LangChain Tavily Search

[![PyPI version](https://badge.fury.io/py/langchain-tavily.svg)](https://badge.fury.io/py/langchain-tavily)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/langchain-tavily)](https://pepy.tech/project/langchain-tavily)

This package contains the LangChain integration with [Tavily Search API](https://tavily.com/)

```bash
pip install -U langchain-tavily
```

---

## Installation

```bash
pip install -U langchain-tavily
```

### Credentials

We also need to set our Tavily API key. You can get an API key by visiting [this site](https://app.tavily.com/sign-in) and creating an account.

```bash
import getpass
import os

if not os.environ.get("TAVILY_API_KEY"):
    os.environ["TAVILY_API_KEY"] = getpass.getpass("Tavily API key:\n")
```

## Tavily Search

Here we show how to instantiate an instance of the Tavily search tool. The tool accepts various parameters to customize the search. After instantiation we invoke the tool with a simple query. This tool allows you to complete search queries using Tavily's Search API endpoint.

### Instantiation

The tool accepts various parameters during instantiation:

- `max_results` (optional, int): Maximum number of search results to return. Default is 5.
- `topic` (optional, str): Category of the search. Can be "general", "news", or "finance". Default is "general".
- `include_answer` (optional, bool | str): Include an answer to original query in results. Default is False. String options include "basic" (quick answer) or "advanced" (detailed answer). If True, defaults to "basic".
- `include_raw_content` (optional,  bool | str): Include the cleaned and parsed HTML content of each search result. "markdown" returns search result content in markdown format. "text" returns the plain text from the results and may increase latency. If True, defaults to "markdown"
- `include_images` (optional, bool): Include a list of query related images in the response. Default is False.
- `include_image_descriptions` (optional, bool): Include descriptive text for each image. Default is False.
- `include_favicon` (optional, bool): Whether to include the favicon URL for each result. Default is False.
- `search_depth` (optional, str): Depth of the search, either "basic" or "advanced". Default is "basic".
- `time_range` (optional, str): The time range back from the current date to filter results - "day", "week", "month", or "year". Default is None.
- `include_domains` (optional, List[str]): List of domains to specifically include. Default is None.
- `exclude_domains` (optional, List[str]): List of domains to specifically exclude. Default is None.
- `country` (optional, str): Boost search results from a specific country. This will prioritize content from the selected country in the search results. Available only if topic is general.

For a comprehensive overview of the available parameters, refer to the [Tavily Search API documentation](https://docs.tavily.com/documentation/api-reference/endpoint/search)

```python
from langchain_tavily import TavilySearch

tool = TavilySearch(
    max_results=5,
    topic="general",
    # include_answer=False,
    # include_raw_content=False,
    # include_images=False,
    # include_image_descriptions=False,
    # include_favicon=False,
    # search_depth="basic",
    # time_range="day",
    # include_domains=None,
    # exclude_domains=None,
    # country=None
)
```

### Invoke directly with args

The Tavily search tool accepts the following arguments during invocation:

- `query` (required): A natural language search query
- The following arguments can also be set during invocation : `include_images`, `include_favicon`, `search_depth` , `time_range`, `include_domains`, `exclude_domains`
- For reliability and performance reasons, certain parameters that affect response size cannot be modified during invocation: `include_answer` and `include_raw_content`. These limitations prevent unexpected context window issues and ensure consistent results.

NOTE: If you set an argument during instantiation this value will persist and overwrite the value passed during invocation.

```python
# Basic query
tool.invoke({"query": "What happened at the last wimbledon"})
```

output:

```bash
{
 'query': 'What happened at the last wimbledon',
 'follow_up_questions': None,
 'answer': None,
 'images': [],
 'results':
 [{'url': 'https://en.wikipedia.org/wiki/Wimbledon_Championships',
   'title': 'Wimbledon Championships - Wikipedia',
   'content': 'Due to the COVID-19 pandemic, Wimbledon 2020 was cancelled ...',
   'score': 0.62365627198,
   'raw_content': None},
    ......................................................................
    {'url': 'https://www.cbsnews.com/news/wimbledon-men-final-carlos-alcaraz-novak-djokovic/',
    'title': "Carlos Alcaraz beats Novak Djokovic at Wimbledon men's final to ...",
    'content': 'In attendance on Sunday was Catherine, the Princess of Wales ...',
    'score': 0.5154731446,
    'raw_content': None}],
  'response_time': 2.3
}
```

### Agent Tool Calling

We can use our tool directly with an agent executor by binding the tool to the agent. This gives the agent the ability to dynamically set the available arguments to the Tavily search tool.

In the below example when we ask the agent to find "What is the most popular sport in the world? include only wikipedia sources" the agent will dynamically set the arguments and invoke Tavily search tool : Invoking `tavily_search` with `{'query': 'most popular sport in the world', 'include_domains': ['wikipedia.org'], 'search_depth': 'basic'}`

```python
# !pip install -qU langchain langchain-openai langchain-tavily
from typing import Any, Dict, Optional
import datetime

from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain.schema import HumanMessage, SystemMessage

# Initialize LLM
llm = init_chat_model(model="gpt-4o", model_provider="openai", temperature=0)

# Initialize Tavily Search Tool
tavily_search_tool = TavilySearch(
    max_results=5,
    topic="general",
)

# Set up Prompt with 'agent_scratchpad'
today = datetime.datetime.today().strftime("%D")
prompt = ChatPromptTemplate.from_messages([
    ("system", f"""You are a helpful research assistant, you will be given a query and you will need to
    search the web for the most relevant information. The date today is {today}."""),
    MessagesPlaceholder(variable_name="messages"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),  # Required for tool calls
])

# Create an agent that can use tools
agent = create_openai_tools_agent(
    llm=llm,
    tools=[tavily_search_tool],
    prompt=prompt
)

# Create an Agent Executor to handle tool execution
agent_executor = AgentExecutor(agent=agent, tools=[tavily_search_tool], verbose=True)

user_input = "What is the most popular sport in the world? include only wikipedia sources"

# Construct input properly as a dictionary
response = agent_executor.invoke({"messages": [HumanMessage(content=user_input)]})
```
