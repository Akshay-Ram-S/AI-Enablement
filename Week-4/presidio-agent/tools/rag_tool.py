from langchain_chroma import Chroma
from langchain_aws import BedrockEmbeddings, ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
import os


CHROMA_DIR = "vectorstore/hr_policy_chroma"
COLLECTION_NAME = "Presidio_HR_Policy_Document"

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def load_rag_chain():
    embeddings = BedrockEmbeddings(
        model_id="amazon.titan-embed-text-v1"
    )

    vectordb = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )

    retriever = vectordb.as_retriever(search_kwargs={"k": 4})

    llm = ChatBedrock(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        region_name=os.environ.get("AWS_REGION"),
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        model_kwargs={"temperature": 0.0}
    )

    prompt = ChatPromptTemplate.from_template(
        """You are an internal HR compliance assistant.

        Answer ONLY from the context.
        If not found, say "Not found in policy documents."

        Context:
        {context}

        Question:
        {question}
        """
    )

    return (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
    )
