from langchain.tools import tool
from config import get_llm
from rag.it_rag import load_it_rag_chain
from rag.finance_rag import load_finance_rag_chain
from tools.tavily_tool import tavily_search
from langchain.agents import create_agent
from typing import Dict, Any


def _fetch_docs_with_fallback(retriever, db, query):
    """
    Try multiple retrieval APIs depending on langchain version:
    1. retriever.get_relevant_documents(query)
    2. retriever.retrieve(query)
    3. db.similarity_search(query, k=...)
    Return list of Document-like objects (with page_content).
    """
    try:
        if hasattr(retriever, "get_relevant_documents"):
            return retriever.get_relevant_documents(query)

        if hasattr(retriever, "retrieve"):
            return retriever.retrieve(query)

        if hasattr(db, "similarity_search"):
            return db.similarity_search(query, k=4)
    
    except Exception as e:
        print(f"Exception: {e}")

    return []


@tool("search_it_documents")
def search_it_documents(query: str) -> str:
    """
    Search internal IT company documents including IT policies,
    troubleshooting guides, technical procedures, software installation guides,
    network configurations, server management, and VPN setup instructions.
    Use this for IT-related questions about company infrastructure, software, hardware, or technical support.
    """
    try:
        retriever, db, _ = load_it_rag_chain()
        docs = _fetch_docs_with_fallback(retriever, db, query)
        return "\n".join(d.page_content for d in docs) if docs else "No relevant IT documents found."
    except Exception as e:
        return f"Error accessing IT documents: {str(e)}"


@tool("search_finance_documents")
def search_finance_documents(query: str) -> str:
    """
    Search internal Finance company documents including payroll information,
    reimbursement policies, budget guidelines, expense procedures, invoice processing,
    and financial policies. Use this for finance-related questions about company 
    financial processes, policies, or procedures.
    """
    try:
        retriever, db, _ = load_finance_rag_chain()
        docs = _fetch_docs_with_fallback(retriever, db, query)
        return "\n".join(d.page_content for d in docs) if docs else "No relevant Finance documents found."
    except Exception as e:
        return f"Error accessing Finance documents: {str(e)}"


@tool("web_search")
def web_search(query: str) -> str:
    """
    Search the web for external information when internal company documents 
    do not contain the answer. Use this for general knowledge, external resources,
    or when you need up-to-date information not available in company documents.
    """
    try:
        return tavily_search(query)
    except Exception as e:
        return f"Error performing web search: {str(e)}"


def dynamic_routing_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dynamic routing agent that intelligently selects and uses appropriate tools
    based on the query content. Instead of pre-routing to specific agents,
    this agent analyzes the query and dynamically chooses which tools to use.
    """
    llm = get_llm()
    query = state["query"] if isinstance(state, dict) else state

    system_prompt = f"""
You are an intelligent support agent for a corporate company. A user has asked: "{query}"

You have access to multiple tools that can help answer questions:

1. **search_it_documents**: Use for IT-related queries about:
   - Software installation, troubleshooting, or technical issues
   - Network problems, VPN setup, or server management
   - Hardware support, laptop issues, or technical procedures
   - Company IT policies and technical documentation

2. **search_finance_documents**: Use for Finance-related queries about:
   - Payroll, salary, or compensation questions
   - Reimbursement policies and expense procedures
   - Budget guidelines and financial processes
   - Invoice processing and financial policies

3. **web_search**: Use when:
   - Internal documents don't contain the answer
   - You need external or public information only related to IT/Finance topics
   - The query requires up-to-date information not in company docs

**Instructions:**
1. Analyze the user's query to understand what type of information they need
2. Choose the most appropriate tool(s) based on the query content
3. You can use multiple tools if needed (e.g., check internal docs first, then web search)
4. Prioritize internal company documents over web search when applicable
5. Never hallucinate - if tools don't provide relevant information, say "Information not found"
6. Provide clear, step-by-step answers when explaining procedures
7. Keep responses professional and concise
8. Answer directly without greeting or asking how you can help

Please don't reveal the internal decision-making process and tool names - just provide the final answer.
Think carefully about which tool(s) to use based on the query content, then provide a helpful answer.

"""

    # Create agent with all available tools
    agent = create_agent(
        llm,
        tools=[search_it_documents, search_finance_documents, web_search],
        system_prompt=system_prompt
    )

    # Let the agent dynamically choose tools and provide response
    try:
        result = agent.invoke({"input": f"Please help me with: {query}"})
        
        # Extract the final answer from the agent result
        answer = next(
            msg.content for msg in reversed(result["messages"])
            if msg.type == "ai"
        )
        
        return {
            "query": query,
            "route": "DYNAMIC",
            "response": answer
        }
        
    except Exception as e:
        return {
            "query": query,
            "route": "DYNAMIC", 
            "response": f"Error processing query: {str(e)}"
        }
