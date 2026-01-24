import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_aws import BedrockEmbeddings

load_dotenv()

PDF_PATH = "data/IT_policy.pdf"
CHROMA_DIR = "vectorstore/it_chroma"
COLLECTION = "IT_policy"

def vectorize():
    docs = PyPDFLoader(PDF_PATH).load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(docs)

    valid_chunks = [
        c for c in chunks if c.page_content and c.page_content.strip()
    ]

    if not valid_chunks:
        raise ValueError("No valid IT text found for embedding")

    embeddings = BedrockEmbeddings(
        model_id="amazon.titan-embed-text-v1",
        region_name=os.environ["AWS_REGION"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )

    db = Chroma.from_documents(
        documents=valid_chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
        collection_name=COLLECTION
    )

    print(f"IT docs indexed: {len(valid_chunks)} chunks")

if __name__ == "__main__":
    vectorize()
