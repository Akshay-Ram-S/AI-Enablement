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

    system_prompt = f"""
You are an IT support agent for a corporate company. A user has asked: "{query}"

Your task is to provide a helpful answer to this specific question.

Rules:
1. Always prioritize INTERNAL IT COMPANY DOCUMENTS first.
2. If there are any external or public data asked by the user, use Web search.
3. Never hallucinate.
4. If neither internal documents nor web results contain the answer,
   reply exactly: "Information not found."
5. Answer clearly and step-by-step, explaining procedures when necessary.
6. Reference IT policies, troubleshooting guides, or procedures when applicable.
7. Keep responses professional and concise.
8. Do not greet the user or ask how you can help - just answer the question directly.

Please search for information and provide a direct answer to the user's question.
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
