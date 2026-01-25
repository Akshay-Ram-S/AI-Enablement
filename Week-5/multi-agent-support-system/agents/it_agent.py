from langchain.tools import tool
from config import get_llm
from rag.it_rag import load_it_rag_chain
from tools.tavily_tool import tavily_search
from langchain.agents import create_agent

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


@tool("internal_it_search")
def internal_it_search(query: str) -> str:
    """
    Search internal IT company documents such as IT policies,
    troubleshooting guides, and technical procedures.
    """
    try:
        retriever, db, _ = load_it_rag_chain()
        docs = _fetch_docs_with_fallback(retriever, db, query)
        return "\n".join(d.page_content for d in docs) if docs else ""
    except Exception:
        return ""


@tool("web_search")
def web_search(query: str) -> str:
    """Search the web if internal IT documents do not contain the answer."""
    return tavily_search(query)

def it_agent(state):
    llm = get_llm()
    query = state["query"] if isinstance(state, dict) else state

    system_prompt = f"""You are an IT Support Agent. The user has asked: "{query}"

MANDATORY PROCESS - FOLLOW THIS EXACT ORDER:

STEP 1: ALWAYS start by using internal_it_search to search company IT documentation first
STEP 2: Review the internal search results carefully  
STEP 3: If internal documents provide sufficient information, answer based ONLY on internal documents
STEP 4: If internal documents are incomplete or empty and you require public data, THEN use web_search for additional IT-related information
STEP 5: Combine internal and external information if both were needed

CRITICAL: You MUST use internal_it_search first before considering web search. Never skip internal search.

If the question is not IT-related, respond: "I'm an IT Support Agent and can only help with IT-related questions about company policies, technical support, hardware, software, and network issues."

Answer the user's question: "{query}"
"""

    agent = create_agent(
        llm,
        tools=[internal_it_search, web_search],
        system_prompt=system_prompt
    )

    result = agent.invoke({"input": f"Please help me with: {query}"})

    answer = next(
            msg.content for msg in reversed(result["messages"])
            if msg.type == "ai"
        )

    return {
        "query": query,
        "route": "IT",
        "response": answer
    }
