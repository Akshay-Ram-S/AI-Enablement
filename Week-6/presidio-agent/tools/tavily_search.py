from langchain_tavily import TavilySearch
from dotenv import load_dotenv
load_dotenv()

tool = TavilySearch(
    max_results=3,
    topic="general",
)

def tavily_search_tool(query: str) -> str:
    """Get general web search information using Tavily."""
    return tool.run(query)