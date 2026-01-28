from agent import agent
import asyncio

from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

langfuse= Langfuse()

async def main():
    print("🧠 Agent is running. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break

        langfuse_handler = CallbackHandler()

        response = await agent.ainvoke({
            "messages": [
                ("user", user_input)
            ]
        },
        {"callbacks": [langfuse_handler]},)

        final_message = next(
            msg.content for msg in reversed(response["messages"])
            if msg.type == "ai"
        )

        print("\nAgent:", final_message, "\n")


if __name__ == "__main__":
    asyncio.run(main())
