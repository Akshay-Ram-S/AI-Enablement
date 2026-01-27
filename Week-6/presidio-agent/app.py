import logging
import asyncio

from agent import llm  # your ChatOpenAI / LLM
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from guardrails import Guard
from guardrails.hub import RegexMatch, ToxicLanguage

# Silence noisy logs
logging.getLogger("opentelemetry").setLevel(logging.ERROR)
logging.getLogger("mcp").setLevel(logging.WARNING)

# Langfuse
langfuse = Langfuse()


def build_chain():
    # -----------------------------
    # 1️⃣ Guardrails definition
    # -----------------------------

    guard = Guard().use_many(
        RegexMatch(
            regex=r"^(hi|hello|hey|hola|good (morning|afternoon|evening))$",
            on_fail="exception"
        ),
        ToxicLanguage(
            on_fail="filter",
        ),
    )

    # -----------------------------
    # 2️⃣ Prompt + parser
    # -----------------------------
    prompt = ChatPromptTemplate.from_template(
        "Answer this question: {question}"
    )

    output_parser = StrOutputParser()

    # -----------------------------
    # 3️⃣ LCEL chain
    # -----------------------------
    chain = (
        prompt
        | llm
        | guard.to_runnable()
        | output_parser
    )

    return chain


async def main():
    print("🧠 Presidio Agent with Guardrails-AI (LCEL) running. Type 'exit' to quit.")

    chain = build_chain()
    langfuse_handler = CallbackHandler()

    while True:
        question = input("You: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("👋 Have a nice day!")
            break

        try:
            # Invoke LCEL chain
            result = chain.invoke(
                {"question": question},
                config={"callbacks": [langfuse_handler]},
            )

            print(f"\nAgent: {result}\n")

        except Exception as e:
            print(f"\n🚫 Guardrails-AI blocked or failed: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
