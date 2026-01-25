from config import get_llm
from typing import Dict, Any

def supervisor_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Supervisor Agent - Classifies user queries as IT or Finance and routes to appropriate specialist agent.
    """
    llm = get_llm()
    query = state["query"] if isinstance(state, dict) else state
    
    system_prompt = f"""You are a Supervisor Agent that classifies user queries and routes them to the appropriate specialist.

User Query: "{query}"

Your task is to classify this query based on the content.

IT-related topics include:
- VPN setup and network issues
- Software installation and troubleshooting
- Hardware requests (laptops, equipment)
- Technical procedures and policies
- Server management and configurations
- Password and security issues
- Cybersecurity threats and best practices

Finance-related topics include:
- Payroll and salary questions
- Reimbursement procedures
- Budget reports and financial data
- Expense policies and procedures
- Invoice processing
- Financial policies and guidelines
- Tax rates and financial regulations

NON-RELEVANT topics include:
- Weather, sports, cooking, entertainment
- General knowledge questions unrelated to business
- Personal advice or non-work related queries

Respond with ONLY one word: "IT", "FINANCE", or "IRRELEVANT"
"""

    try:
        response = llm.invoke(system_prompt)
        route = response.content.strip().upper()
        
        # Ensure we get a valid route
        if route not in ["IT", "FINANCE"]:
            # Default to IT if unclear
            route = "IT"
            
        return {
            "query": query,
            "route": route,
            "response": ""
        }
        
    except Exception as e:
        return {
            "query": query,
            "route": "IT",
            "response": f"Error in routing: {str(e)}"
        }


def dynamic_routing_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    return supervisor_agent(state)
