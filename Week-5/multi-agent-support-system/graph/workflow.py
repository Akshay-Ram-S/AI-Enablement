from langgraph.graph import StateGraph
from agents.routing_agent import supervisor_agent
from agents.it_agent import it_agent
from agents.finance_agent import finance_agent

def route_to_agent(state):
    """Route based on supervisor's classification"""
    route = state.get("route", "IT")
    if route == "FINANCE":
        return "finance_agent"
    elif route == "IRRELEVANT":
        return "irrelevant_handler"
    else:
        return "it_agent"

def irrelevant_handler(state):
    """Handle queries outside IT/Finance scope"""
    return {
        "query": state["query"],
        "route": "IRRELEVANT",
        "response": "I'm a corporate support system that handles IT and Finance-related queries only. For questions about weather, sports, cooking, or other non-business topics, please use appropriate external resources or contact the relevant department."
    }

def create_supervisor_workflow():
    """
    Creates a supervisor-agent workflow:
    1. Supervisor Agent classifies queries as IT, Finance, or Irrelevant
    2. Routes to appropriate specialist agent or irrelevant handler
    3. Specialist agents use their tools to provide responses
    """
    graph = StateGraph(dict)

    # Add nodes
    graph.add_node("supervisor", supervisor_agent)
    graph.add_node("it_agent", it_agent)
    graph.add_node("finance_agent", finance_agent)
    graph.add_node("irrelevant_handler", irrelevant_handler)

    # Set entry point
    graph.set_entry_point("supervisor")

    # Add conditional routing from supervisor to specialist agents
    graph.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "it_agent": "it_agent",
            "finance_agent": "finance_agent",
            "irrelevant_handler": "irrelevant_handler"
        }
    )

    # All agents are end points
    graph.set_finish_point("it_agent")
    graph.set_finish_point("finance_agent")
    graph.set_finish_point("irrelevant_handler")

    return graph.compile()

# Create the compiled app
app = create_supervisor_workflow()

# Keep the old function for backward compatibility
def create_dynamic_workflow():
    return create_supervisor_workflow()
