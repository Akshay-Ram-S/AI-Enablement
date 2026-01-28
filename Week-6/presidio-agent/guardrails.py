from typing import Any
from langchain.agents.middleware import before_agent, AgentState
from langgraph.runtime import Runtime
from langchain.agents.middleware import after_agent
from langchain.messages import AIMessage
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
load_dotenv()

banned_keywords = ["hack", "exploit", "malware"]

def _content_filter_logic(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Deterministic guardrail logic: Block requests containing banned keywords."""
    # Get the first user message
    if not state["messages"]:
        return None

    first_message = state["messages"][0]
    if first_message.type != "human":
        return None

    content = first_message.content.lower()

    # Check for banned keywords
    for keyword in banned_keywords:
        if keyword in content:
            # Block execution before any processing
            return {
                "messages": [{
                    "role": "assistant",
                    "content": "Sorry, I cannot process requests containing inappropriate content."
                }],
                "jump_to": "end"
            }

    return None

@before_agent(can_jump_to=["end"])
def content_filter(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Deterministic guardrail: Block requests containing banned keywords."""
    return _content_filter_logic(state, runtime)


# Use the same Bedrock model for consistency
safety_model = init_chat_model("gpt-4o-mini")

def _safety_guardrail_logic(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Model-based guardrail logic: Use an LLM to evaluate response safety."""
    # Get the final AI response
    if not state["messages"]:
        return None

    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage):
        return None

    # Use a model to evaluate safety
    safety_prompt = f"""Evaluate if this response is safe and appropriate.
    Respond with only 'SAFE' or 'UNSAFE'.

    Response: {last_message.content}"""

    result = safety_model.invoke([{"role": "user", "content": safety_prompt}])

    if "UNSAFE" in result.content:
        # Properly stop execution and return safe response
        return {
            "messages": state["messages"][:-1] + [{
                "role": "assistant", 
                "content": "Sorry, I cannot provide that response."
            }],
            "jump_to": "end"
        }

    return None

@after_agent(can_jump_to=["end"])
def safety_guardrail(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Model-based guardrail: Use an LLM to evaluate response safety."""
    return _safety_guardrail_logic(state, runtime)
