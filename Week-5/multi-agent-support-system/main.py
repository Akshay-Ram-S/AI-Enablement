# Interactive main that uses dynamic routing agent to handle queries
from agents.routing_agent import dynamic_routing_agent
from graph.workflow import app

def route_query(query: str) -> str:
    """
    Route query using the dynamic routing agent that intelligently
    selects appropriate tools based on query content.
    """
    try:
        # Option 1: Use the workflow app
        result = app.invoke({"query": query})
        return result.get("response", "No response generated.")
        
    except Exception as e:
        # Option 2: Fallback to direct agent call
        try:
            state = {"query": query}
            result = dynamic_routing_agent(state)
            return result.get("response", "No response generated.")
        except Exception as fallback_e:
            return f"Error processing query: {str(e)}. Fallback error: {str(fallback_e)}"

def main_loop():
    print("\nMulti-agent support system. Type your question and press Enter.")
    print("Type 'exit' (or Ctrl+C) to quit.\n")
    try:
        while True:
            query = input("Ask a question (or 'exit'): ").strip()
            if not query:
                continue
            if query.lower() == "exit":
                print("Goodbye.")
                break

            answer = route_query(query)

            print("\nAnswer:\n", answer or "No response returned.")
            print()
    
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting...")

if __name__ == "__main__":
    main_loop()
