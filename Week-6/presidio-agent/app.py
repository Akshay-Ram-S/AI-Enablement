import asyncio
import logging

from agent import agent, llm
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

from nemoguardrails import RailsConfig, LLMRails

# Reduce noise
logging.getLogger("mcp").setLevel(logging.WARNING)

langfuse = Langfuse()


def load_guardrails():
    try:
        config = RailsConfig.from_path("guardrails")
        return LLMRails(config=config, llm=llm)
    except Exception as e:
        print(f"Guardrails initialization failed: {e}")
        return None


async def invoke_agent(user_input: str, callbacks):
    response = await agent.ainvoke(
        {"messages": [("user", user_input)]},
        {"callbacks": callbacks},
    )

    return next(
        msg.content
        for msg in reversed(response["messages"])
        if msg.type == "ai"
    )


async def main():
    print("🧠 Presidio Agent with Unified Guardrails is running. Type 'exit' to quit.")

    rails = load_guardrails()
    if not rails:
        print("Guardrails not available. Exiting.")
        return

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Bye, have a nice day!")
            break

        langfuse_handler = CallbackHandler()

        try:
            # 🔒 SINGLE Guardrails entry point
            rails_decision = await rails.generate_async(
                messages=[{"role": "user", "content": user_input}]
            )

            # Guardrails blocked the request (input flows)
            if rails_decision and rails_decision.get("role") == "assistant":
                print("\nGuardrails: Blocked content, violation of policies\n")
                continue

            # 🤖 Agent is allowed to run
            agent_output = await invoke_agent(
                user_input, [langfuse_handler]
            )

            # 🔒 Pass agent output THROUGH Guardrails ONCE (same decision surface)
            rails_output = await rails.generate_async(
                messages=[{"role": "assistant", "content": agent_output}]
            )

            # Output blocked
            if rails_output and rails_output.get("role") == "assistant":
                print("\nGuardrails: Blocked content, violation of policies\n")
                continue

            print(f"\nAgent: {agent_output}\n")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
