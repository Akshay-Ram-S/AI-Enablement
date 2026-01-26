import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_aws import BedrockEmbeddings

load_dotenv()

DATA_DIR = "data"
CHROMA_DIR = "vectorstore/hr_policy_chroma"
COLLECTION_NAME = "Presidio_HR_Policy_Document"

def vectorize_policies():
    documents = []

    for file in os.listdir(DATA_DIR):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(DATA_DIR, file))
            documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(documents)

    embeddings = BedrockEmbeddings(
        model_id="amazon.titan-embed-text-v1"
    )

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
        collection_name=COLLECTION_NAME
    )

    print(f"Stored {len(chunks)} chunks in ChromaDB")

if __name__ == "__main__":
    vectorize_policies()
