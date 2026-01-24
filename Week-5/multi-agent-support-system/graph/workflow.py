from langgraph.graph import StateGraph
from agents.routing_agent import dynamic_routing_agent

def create_dynamic_workflow():
    """
    Creates a simplified workflow using the dynamic routing agent.
    Instead of routing to separate IT and Finance agents, the dynamic agent
    intelligently chooses which tools to use based on the query content.
    """
    graph = StateGraph(dict)

    # Add single dynamic routing agent node
    graph.add_node("dynamic_agent", dynamic_routing_agent)

    # Set entry and finish points
    graph.set_entry_point("dynamic_agent")
    graph.set_finish_point("dynamic_agent")

    return graph.compile()

# Create the compiled app
app = create_dynamic_workflow()
