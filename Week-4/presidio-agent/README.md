```md
# Presidio Internal Research Agent 🤖

Presidio Internal Research Agent is a **multi-tool AI assistant** designed to answer internal HR, compliance, insurance, and external industry-related questions using:

- **RAG over internal HR policy PDFs**
- **Google Docs (via MCP) for insurance documents**
- **Tavily web search for external/industry queries**

The agent intelligently selects the correct tool based on the question type and responds strictly from authoritative sources.

---

## 📁 Project Structure

```

presidio-agent/
│
├── data/
│   └── hr policy.pdf
│
├── tools/
│   ├── rag_tool.py
│   ├── tavily_search.py
│   ├── vectorize_policies.py
│   └── mcp_google_docs.py
│
├── agent.py
├── app.py
├── requirements.txt
├── credentials.json        # Google OAuth (not committed)
├── token.json              # Generated after OAuth
└── .env

````

---

## 🧠 How the System Works (High-Level)

### 1. **HR Policy Questions (RAG)**
- HR policy PDFs are embedded using **Amazon Titan Embeddings**
- Stored in **ChromaDB**
- Queried semantically using LangChain
- Answers are **strictly grounded in policy text**

### 2. **Insurance Questions (Google Docs via MCP)**
- Google Docs are accessed via **MCP (Model Context Protocol)**
- OAuth-based Google Docs API access
- Relevant sentences are extracted and ranked by keyword overlap

### 3. **External / Industry Questions**
- Uses **Tavily Search API**
- Suitable for regulations, benchmarks, trends, and market data

### 4. **Tool Selection Logic**
Defined in `SYSTEM_PROMPT` inside `agent.py`:
- HR / internal → `rag_search`
- Insurance → `google_doc_search`
- External → `tavily_search`

The agent **must use tools** and never hallucinates answers.

---

## ⚙️ Prerequisites

- Python **3.10+**
- AWS account with **Amazon Bedrock enabled**
- Google Cloud Project with **Google Docs API enabled**
- Tavily API key

---

## 🔐 Environment Variables (`.env`)

Create a `.env` file in the project root:

```env
# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Tavily
TAVILY_API_KEY=your_tavily_key

# Google Docs
INSURANCE_DOC_IDS=doc_id_1,doc_id_2
````

---

## 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 📄 Vectorize HR Policy PDFs (One-Time Setup)

Before running the agent, convert HR PDFs into vector embeddings:

```bash
python tools/vectorize_policies.py
```

This will:

* Load PDFs from `data/`
* Split them into chunks
* Store embeddings in `vectorstore/hr_policy_chroma`

---

## 🔑 Google OAuth Setup (One-Time)

1. Create OAuth credentials in **Google Cloud Console**
2. Download `credentials.json`
3. Place it in the project root
4. First run will open a browser for authentication
5. `token.json` will be generated automatically

---

## 🚀 Run the Agent

```bash
python app.py
```

You’ll see:

```text
🧠 Agent is running. Type 'exit' to quit.
```

Ask questions interactively.

---


