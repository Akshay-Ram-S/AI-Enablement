import asyncio
import logging

from agent import agent, llm  # llm = ChatBedrock
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

from nemoguardrails import RailsConfig, LLMRails

# Suppress MCP server logs
logging.getLogger("mcp").setLevel(logging.WARNING)

# Initialize Langfuse client
langfuse = Langfuse()


def load_guardrails():
    try:
        config = RailsConfig.from_path("guardrails")
        return LLMRails(config=config, llm=llm)
    except Exception as e:
        print(f"❌ Guardrails initialization failed: {e}")
        return None


async def main():
    print("🧠 Presidio Agent with Guardrails is running. Type 'exit' to quit.")

    rails = load_guardrails()
    guardrails_enabled = rails is not None

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break

        langfuse_handler = CallbackHandler()

        try:
            if guardrails_enabled:
                rails_response = await rails.generate_async(
                    messages=[{"role": "user", "content": user_input}],
                )

                # If guardrails blocked → response comes from bot flow
                if rails_response and rails_response.get("role") == "assistant":
                    print("\n🚫 Guardrails: Blocked by Guardrails\n")
                    continue

            agent_response = await agent.ainvoke(
                {"messages": [("user", user_input)]},
                {"callbacks": [langfuse_handler]},
            )

            final_message = next(
                msg.content
                for msg in reversed(agent_response["messages"])
                if msg.type == "ai"
            )

            if guardrails_enabled:
                rails_output = await rails.generate_async(
                    messages=[{"role": "assistant", "content": final_message}],
                )

                if rails_output and rails_output.get("role") == "assistant":
                    print(f"\n🚫 Guardrails: {rails_output['content']}\n")
                    continue

            print(f"\n✅ Agent: {final_message}\n")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
