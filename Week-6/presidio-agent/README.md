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
├── data/
│   └── hr_policy.pdf
├── tools/
│   ├── rag_tool.py
│   ├── tavily_search.py
│   ├── vectorize_policies.py
│   └── mcp_google_docs.py
├── vectorstore/
│   └── hr_policy_chroma/        # Generated after running vectorize_policies.py
├── agent.py                     # Main agent with middleware integration
├── app.py                       # Interactive CLI application
├── guardrails.py                # Security middleware (content filter & safety guardrail)
├── test_guardrails.py           # Comprehensive guardrails test suite
├── requirements.txt
├── credentials.json              # Google OAuth (not committed - add to .gitignore)
├── token.json                    # Generated after OAuth (add to .gitignore)
├── .env                          # Environment variables (add to .gitignore)
└── .gitignore
```

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

## 🛡️ Security & Guardrails

The Presidio Agent implements a **4-layer security middleware system** that automatically protects against malicious inputs and unsafe outputs:

### 🔒 Layer 1: Content Filter (Input Protection)
- **Blocks banned keywords** before any processing
- **Keywords**: `hack`, `exploit`, `malware` (case-insensitive)
- **Action**: Immediately stops execution and returns safe message
- **Example**: `"How to hack systems?"` → `"I cannot process requests containing inappropriate content. Please rephrase your request."`

### 🔒 Layer 2: PII Protection (Data Privacy)
- **Redacts sensitive information** from inputs and outputs
- **Protected Data**: Email addresses, phone numbers, SSNs
- **Strategy**: Automatic detection and redaction
- **Bidirectional**: Protects both user inputs and AI responses

### 🔒 Layer 3: Human-in-the-Loop (Critical Actions)
- **Requires human approval** for sensitive operations
- **Triggers**: Email sending, data deletion, system modifications
- **Workflow**: Agent pauses and waits for explicit user confirmation
- **Safety**: Prevents autonomous execution of high-risk actions

### 🔒 Layer 4: Safety Guardrail (Output Validation)
- **AI-powered response evaluation** using Claude model
- **Process**: Every AI response is evaluated for safety/appropriateness
- **Detection**: Harmful, biased, or inappropriate content
- **Action**: Unsafe responses are blocked and replaced with safe alternatives

### 🧪 Testing Your Guardrails

Run the comprehensive test suite to verify all guardrails are working:

```bash
python test_guardrails.py
```

**Expected Output:**
```
🎉 ALL TESTS PASSED! Your guardrails are working correctly.

💡 Your guardrails will:
   - Block requests containing 'hack', 'exploit', or 'malware'
   - Evaluate AI responses for safety using Claude
   - Properly stop execution when issues are detected
```

### 🔧 Guardrails Configuration

Guardrails are automatically integrated into the agent middleware:

```python
middleware=[
    content_filter,           # Input filtering
    PIIMiddleware(...),       # PII redaction
    HumanInTheLoopMiddleware(...), # Human approval
    safety_guardrail,         # Output validation
]
```

**No manual intervention required** - all protections work automatically on every agent interaction.

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
```

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
- Load PDFs from `data/`
- Split them into chunks
- Store embeddings in `vectorstore/hr_policy_chroma`

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

You'll see:

```text
🧠 Agent is running. Type 'exit' to quit.
```

Ask questions interactively.

---
