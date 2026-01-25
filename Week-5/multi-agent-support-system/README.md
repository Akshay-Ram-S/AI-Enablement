# Multi-Agent Support System

A dynamic multi-agent support system that intelligently routes user queries to appropriate resources using AI-powered document retrieval and web search capabilities. The system specializes in IT and Finance support queries, leveraging internal company documents and external knowledge sources.

## Workflow Design

The Multi-Agent Support System uses a streamlined workflow to intelligently route and process user queries through specialized domain agents.

### High-Level System Flow

```
┌─────────────────┐
│   User Query    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Routing Agent   │
│ (Classification)│
└─────────────────┘
         │
    ┌────┼────┐
    │         │
    ▼         ▼
┌─────────┐ ┌─────────┐
│IT Agent │ │Finance  │
│         │ │Agent    │
└─────────┘ └─────────┘
    │         │
    ▼         ▼
┌─────────────────┐
│ Agent Workflow  │
│ 1. Search       │
│    Internal     │
│    Documents    │
│ 2. For external │
│    sources, Web |
|    Search       │
│ 3. Generate     │
│    Response     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Final Response  │
│ to User         │
└─────────────────┘
```


## 🚀 Features

- **Dynamic Routing**: Intelligent agent that selects the most appropriate tools based on query content
- **RAG (Retrieval Augmented Generation)**: Search through internal IT and Finance documents
- **Web Search Integration**: Access external information when internal documents are insufficient
- **AWS Bedrock Integration**: Powered by Claude 3.5 Sonnet for advanced language understanding
- **Interactive CLI**: User-friendly command-line interface for real-time queries
- **Fallback Mechanisms**: Robust error handling with multiple retrieval strategies

## 🏗️ Architecture

### Core Components

```
multi-agent-support-system/
├── main.py                     # Main interactive application
├── config.py                   # AWS Bedrock configuration
├── agents/                     # Agent implementations
│   ├── routing_agent.py        # Dynamic routing logic
│   ├── finance_agent.py        # Finance-specific agent
│   └── it_agent.py            # IT-specific agent
├── rag/                        # RAG implementations
│   ├── finance_rag.py         # Finance document retrieval
│   ├── it_rag.py             # IT document retrieval
│   ├── vectorize_finance.py   # Finance document vectorization
│   └── vectorize_it.py        # IT document vectorization
├── graph/                      # Workflow orchestration
│   └── workflow.py            # LangGraph workflow definition
├── tools/                      # External tools
│   └── tavily_tool.py         # Web search functionality
├── data/                       # Document storage
│   ├── Finance_policy.pdf     # Finance policy documents
│   └── IT_policy.pdf          # IT policy documents
└── vectorstore/               # Vector database storage
```

### Agent Types

1. **Dynamic Routing Agent**: Intelligently selects appropriate tools based on query analysis
2. **IT Agent**: Specialized in technical support, infrastructure, and IT policies
3. **Finance Agent**: Handles payroll, reimbursements, budgets, and financial procedures

### Available Tools

- `search_it_documents`: Search internal IT documentation and policies
- `search_finance_documents`: Search internal Finance documentation and procedures  
- `web_search`: Perform external web searches using Tavily API

## 📋 Prerequisites

- Python 3.10 or higher
- AWS Account with Bedrock access
- Tavily API key (for web search functionality)

## 🛠️ Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd multi-agent-support-system
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Alternative installation using setup.py**:
   ```bash
   pip install -e .
   ```

## ⚙️ Configuration

1. **Create a `.env` file** in the project root with the following variables:
   ```env
   # AWS Bedrock Configuration
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   
   # Tavily API Key (for web search)
   TAVILY_API_KEY=your_tavily_api_key
   ```

2. **Verify AWS Bedrock permissions**: Ensure your AWS credentials have access to:
   - `anthropic.claude-3-5-sonnet-20240620-v1:0` (for chat)
   - `amazon.titan-embed-text-v1` (for embeddings)

3. **Document Setup**: Place your company documents in the `data/` folder:
   - `Finance_policy.pdf`: Finance-related policies and procedures
   - `IT_policy.pdf`: IT-related policies and procedures

## 🚀 Usage

### Interactive Mode

Run the main application for an interactive query session:

```bash
python main.py
```

The system will prompt you to enter queries. Type your questions and press Enter:

```
Multi-agent support system. Type your question and press Enter.
Type 'exit' (or Ctrl+C) to quit.

Ask a question (or 'exit'): How do I set up VPN access on my laptop?

Answer:
Based on the IT policy documents, here are the steps to set up VPN access...
```



### Testing

Run the comprehensive test suite to compare routing approaches:

```bash
python test_routing_agent.py
```

## 🧪 Example Queries

### IT-Related Queries
- "How do I install VPN software on my laptop?"
- "What are the password requirements for company accounts?"
- "How do I connect to the company WiFi?"
- "I'm having network connectivity issues, what should I do?"

### Finance-Related Queries  
- "What is the reimbursement policy for travel expenses?"
- "How do I submit an expense report?"
- "What are the budget approval procedures?"
- "When is payroll processed each month?"

### Mixed or External Queries
- "I need help with payroll and also setting up SSH access"
- "What are the latest cybersecurity trends in 2024?"

## 🔧 Development

### Adding New Documents

1. Add PDF documents to the `data/` folder
2. Run the vectorization scripts:
   ```bash
   python rag/vectorize_finance.py  # For finance documents
   python rag/vectorize_it.py       # For IT documents
   ```

### Extending Functionality

- **Add new agents**: Create new agent files in the `agents/` directory
- **Add new tools**: Implement tools in the `tools/` directory
- **Modify routing logic**: Update `agents/routing_agent.py`
- **Extend RAG capabilities**: Modify files in the `rag/` directory


## 📚 Dependencies

### Core Dependencies
- `langchain`: Framework for LLM applications
- `langgraph`: Graph-based workflow orchestration
- `langchain-aws`: AWS Bedrock integration
- `langchain-community`: Community tools and integrations
- `chromadb`: Vector database for embeddings
- `pypdf`: PDF document processing

### External Services
- `tavily-python`: Web search API
- `python-dotenv`: Environment variable management


**Built with**: LangChain, LangGraph, AWS Bedrock, ChromaDB, and Tavily Search
