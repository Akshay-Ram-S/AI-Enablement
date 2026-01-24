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

    system_prompt = f"""
You are a Finance support agent for a corporate company. A user has asked: "{query}"

Your task is to provide a helpful answer to this specific question.

Rules:
1. Always prioritize INTERNAL FINANCE COMPANY DOCUMENTS first.
2. If there are any external or public data asked by the user, use Web search.
3. Never hallucinate.
4. If neither internal documents nor web results contain the answer,
   reply exactly: "Information not found."
5. Answer clearly and step-by-step.
6. Reference finance policies, forms, or procedures when applicable.
7. Keep responses professional and concise.
8. Do not greet the user or ask how you can help - just answer the question directly.

Please search for information and provide a direct answer to the user's question.
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
