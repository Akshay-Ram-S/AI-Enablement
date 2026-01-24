import os
from tavily import TavilyClient

def tavily_search(query: str) -> str:
    try:
        client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
        result = client.search(
            query=query,
            max_results=5,
            include_answer=True
        )
        return str(result)
    except Exception as e:
        return f"Tavily search unavailable: {str(e)}"
