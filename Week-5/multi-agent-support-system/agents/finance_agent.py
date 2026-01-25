from langchain.tools import tool
from rag.finance_rag import load_finance_rag_chain
from tools.tavily_tool import tavily_search
from langchain.agents import create_agent
from config import get_llm


def _fetch_docs_with_fallback(retriever, db, query):
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


@tool("internal_finance_search")
def internal_finance_search(query: str) -> str:
    """
    Search internal Finance company documents such as payroll,
    reimbursements, budgets, and finance policies.
    """
    try:
        retriever, db, _ = load_finance_rag_chain()
        docs = _fetch_docs_with_fallback(retriever, db, query)
        return "\n".join(d.page_content for d in docs) if docs else ""
    except Exception:
        return ""


@tool("web_search")
def web_search(query: str) -> str:
    """Search the web if internal finance documents do not contain the answer."""
    return tavily_search(query)



def finance_agent(state):
    llm = get_llm()
    query = state["query"] if isinstance(state, dict) else state

    system_prompt = f"""You are a Finance Support Agent. The user has asked: "{query}"

MANDATORY PROCESS - FOLLOW THIS EXACT ORDER:

STEP 1: ALWAYS start by using internal_finance_search to search company finance documentation first
STEP 2: Review the internal search results carefully  
STEP 3: If internal documents provide sufficient information, answer based ONLY on internal documents
STEP 4: If internal documents are incomplete or empty and you require public data, THEN use web_search for public finance-related information
STEP 5: Combine internal and external information if both were needed

CRITICAL: You MUST use internal_finance_search first before considering web search. Never skip internal search.

If the question is not finance-related, respond: "I'm a Finance Support Agent and can only help with finance-related questions about company policies, payroll, expenses, reimbursements, and financial procedures."

Answer the user's question: "{query}"
"""

    agent = create_agent(
        llm,
        tools=[internal_finance_search, web_search],
        system_prompt=system_prompt
    )

    # 🔹 Let agent reason + invoke tools
    result = agent.invoke({"input": f"Please help me with: {query}"})

    # 🔹 Extract clean response from LangChain agent result
    answer = "Information not found."
    
    answer = next(
                msg.content for msg in reversed(result["messages"])
                if msg.type == "ai"
            )

    return {
        "query": query,
        "route": "FINANCE",
        "response": answer
    }
