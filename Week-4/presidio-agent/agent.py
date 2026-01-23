import os
import asyncio
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_aws import ChatBedrockConverse
from tools.tavily_search import tavily_search_tool
from tools.rag_tool import load_rag_chain
from langchain_mcp_adapters.client import MultiServerMCPClient

llm = ChatBedrockConverse(
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    region_name=os.environ.get("AWS_REGION"),
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
)

@tool
def tavily_search(query: str) -> str:
    """
    Perform web search for industry benchmarks, trends and regulatory for Presidio IT company
    in the technology sector using Tavily.
    """
    return tavily_search_tool(query)

@tool
def rag_search(query: str) -> str:
    """
    Search internal HR policy documents using vector embeddings and semantic search.
    
    Use this tool for questions about:
    - Artificial Intelligence Usage Policy
    - Leave and Time Off Policy
    - Recruitment and Hiring Standards
    - Workplace Rules and Conduct Standards
    
    This tool searches through PDF documents stored in the vector database
    and returns the most relevant sections based on semantic similarity.
    
    Args:
        query: The user's question about HR policies or company guidelines
        
    Returns:
        str: Relevant excerpts from HR policy documents
    """
    rag_chain = load_rag_chain()
    result = rag_chain.invoke(query)
    return result



SYSTEM_PROMPT = """
You are Presidio's Internal Research Agent.

RULES:
- For ANY HR related policy, leave, AI usage, compliance, or internal questions,
  you MUST use the rag_search tool.
- For ANY external, industry, regulatory, or trend-related questions,
  you MUST use the tavily_search tool.
- For ANY insurance related questions, you MUST use the google_doc_search tool. 
  Stick to the content in the document
- Always provide answers based on the tool results.
- If multiple tools are used, synthesize the information into a coherent answer.
- If any search returns "Not found", say so explicitly and also question outside presidio is asked, 
  state that you are unable to answer questions outside presidio internal context.
- Keep answers concise and relevant to Presidio's context.
- For generic greetings or non-specific queries, respond politely but do not use any tools.
"""

async def create_presidio_agent():
    client = MultiServerMCPClient(
        {
            "mcpTool": {
                "transport": "stdio",
                "command": "python",
                "args": ["tools/mcp_google_docs.py"],
            }
        }
    )

    mcp_tools = await client.get_tools() 

    agent = create_agent(
        llm,
        tools=[*mcp_tools, tavily_search, rag_search],
        system_prompt=SYSTEM_PROMPT
    )

    return agent


agent = asyncio.run(create_presidio_agent())


