import os
from langchain_chroma import Chroma
from langchain_aws import BedrockEmbeddings, ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from tools.tavily_tool import tavily_search

CHROMA_DIR = "vectorstore/finance_chroma"
COLLECTION = "Finance_policy"

def _format_docs(docs):
    if not docs:
        return ""
    return "\n\n".join(d.page_content for d in docs)

def _web_search(input_dict):
    return tavily_search(input_dict["question"])

def load_finance_rag_chain():
    embeddings = BedrockEmbeddings(
        model_id="amazon.titan-embed-text-v1",
        region_name=os.environ["AWS_REGION"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )

    db = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name=COLLECTION
    )

    retriever = db.as_retriever(search_kwargs={"k": 4})

    llm = ChatBedrock(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        region_name=os.environ["AWS_REGION"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        model_kwargs={"temperature": 0.0}
    )

    prompt = ChatPromptTemplate.from_template(
        """
You are a Finance support assistant.

Use INTERNAL FINANCE POLICIES first.
If information is missing, use WEB SEARCH.

Internal Context:
{context}

Web Context:
{web_context}

Question:
{question}
"""
    )

    chain = (
        {
            "context": retriever | _format_docs,
            "web_context": RunnableLambda(_web_search),
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
    )

    return retriever, db, chain