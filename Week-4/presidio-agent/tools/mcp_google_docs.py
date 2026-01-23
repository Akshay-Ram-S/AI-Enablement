from mcp.server.fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
import re

mcp = FastMCP("Presidio Agent MCP")

SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")

INSURANCE_DOC_ID = "1Nu4mXrtgp_4p3z6ObLtIcyWs4C7OEOhBxCWq6AdSyIk"


def get_docs_service():
    creds = None

    # If token.json exists, load credentials
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no credentials or they are invalid/expired, run OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise RuntimeError(f"{CREDENTIALS_FILE} not found. Cannot run OAuth flow.")
            
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("docs", "v1", credentials=creds)



def extract_text(doc):
    text = []
    content = doc.get("body", {}).get("content", [])

    for element in content:
        paragraph = element.get("paragraph")
        if not paragraph:
            continue

        for el in paragraph.get("elements", []):
            if "textRun" in el:
                text.append(el["textRun"]["content"])

    return "".join(text)


def normalize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [t for t in text.split() if len(t) > 2]


def extract_sentences(text: str) -> list[str]:
    return re.split(r"(?<=[.!?])\s+", text)


def relevance_score(query_tokens, sentence_tokens) -> int:
    return len(set(query_tokens) & set(sentence_tokens))


@mcp.tool()
def doc_search(query: str) -> str:
    """
    Answer insurance-related questions using a single Google Doc.
    """
    try:
        docs_service = get_docs_service()
        doc = docs_service.documents().get(
            documentId=INSURANCE_DOC_ID
        ).execute()

        full_text = extract_text(doc)

        if not full_text.strip():
            return "Not found"

        query_tokens = normalize(query)
        sentences = extract_sentences(full_text)

        scored = []

        for sentence in sentences:
            sentence_tokens = normalize(sentence)
            score = relevance_score(query_tokens, sentence_tokens)

            if score > 0:
                scored.append((score, sentence.strip()))

        if not scored:
            return "Not found"

        scored.sort(key=lambda x: x[0], reverse=True)

        top_results = [s for _, s in scored[:10]]

        return "\n".join(top_results)

    except Exception as e:
        return f"Error reading Google Doc: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
