import os
import asyncio
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_aws import ChatBedrock
from tools.tavily_search import tavily_search_tool
from tools.rag_tool import load_rag_chain
from langchain_mcp_adapters.client import MultiServerMCPClient
from langfuse.langchain import CallbackHandler
from langchain.agents.middleware import PIIMiddleware
from langchain.agents.middleware import HumanInTheLoopMiddleware
from guardrails import content_filter, safety_guardrail

# Initialize Langfuse handler for tracing
langfuse_handler = CallbackHandler()

llm = ChatBedrock(
    model="anthropic.claude-3-5-sonnet-20240620-v1:0",
    region_name=os.environ.get("AWS_REGION"),
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    temperature=0.7,
    max_tokens=4000
)


# Tools
@tool
def tavily_search(query: str) -> str:
    """Perform web search for industry benchmarks, trends, and regulatory updates."""
    return tavily_search_tool(query)

@tool
def rag_search(query: str) -> str:
    """Search internal HR policy documents using RAG."""
    rag_chain = load_rag_chain()
    return rag_chain.invoke(query)

# System prompt to guide agent behavior
SYSTEM_PROMPT = """
You are Presidio's Internal Research Agent.

RULES:
- HR related, compliance, leave, AI usage queries → use rag_search tool.
- External industry/regulatory/trend queries → use tavily_search tool.
- Insurance questions → use MCP Google Docs tool.
- Always answer based on tool results; if multiple tools, synthesize coherently.
- If result is "Not found" or outside Presidio, say so explicitly.
- Keep answers concise and relevant.
"""

# Async function to create the agent
async def create_presidio_agent():
    # Initialize MCP client for Google Docs tool
    client = MultiServerMCPClient(
        {
            "mcpTool": {
                "transport": "stdio",
                "command": "python",
                "args": ["tools/mcp_google_docs.py"],
            }
        }
    )
    # Load MCP tools
    mcp_tools = await client.get_tools()

    # Create agent
    agent = create_agent(
        llm,
        tools=[*mcp_tools, tavily_search, rag_search],
        system_prompt=SYSTEM_PROMPT,
        middleware=[
            # Layer 1: Deterministic input filter (before agent)
            content_filter,

            # Layer 2: PII protection (input and output)
            PIIMiddleware("email", strategy="redact", apply_to_input=True, apply_to_output=True),

            # Layer 3: Human approval for sensitive tools
            HumanInTheLoopMiddleware(interrupt_on={"send_email": True}),

            # Layer 4: Model-based safety check (after agent)
            safety_guardrail,
        ],
    )
    return agent

# Initialize agent
agent = asyncio.run(create_presidio_agent())
