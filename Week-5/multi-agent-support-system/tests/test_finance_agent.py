import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.finance_agent import _fetch_docs_with_fallback, internal_finance_search, web_search, finance_agent


class TestFetchDocsWithFallback:
    """Test cases for the _fetch_docs_with_fallback utility function"""
    
    def test_fetch_docs_success(self):
        """Test successful document fetching"""
        mock_retriever = Mock()
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.page_content = "Finance policy content"
        mock_retriever.get_relevant_documents.return_value = [mock_doc]
        
        result = _fetch_docs_with_fallback(mock_retriever, mock_db, "payroll query")
        assert result == [mock_doc]
    
    def test_fetch_docs_exception_handling(self):
        """Test exception handling returns empty list"""
        mock_retriever = Mock()
        mock_retriever.get_relevant_documents.side_effect = Exception("Database error")
        mock_db = Mock()
        
        result = _fetch_docs_with_fallback(mock_retriever, mock_db, "test query")
        assert result == []


class TestInternalFinanceSearch:
    """Test cases for the internal_finance_search tool"""
    
    @patch('agents.finance_agent.load_finance_rag_chain')
    @patch('agents.finance_agent._fetch_docs_with_fallback')
    def test_internal_finance_search_success(self, mock_fetch_docs, mock_load_rag):
        """Test successful internal finance search"""
        # Mock RAG chain loading
        mock_retriever = Mock()
        mock_db = Mock()
        mock_chain = Mock()
        mock_load_rag.return_value = (mock_retriever, mock_db, mock_chain)
        
        # Mock document fetching
        mock_doc1 = Mock()
        mock_doc1.page_content = "Payroll policy details"
        mock_doc2 = Mock()
        mock_doc2.page_content = "Expense reimbursement process"
        mock_fetch_docs.return_value = [mock_doc1, mock_doc2]
        
        result = internal_finance_search.func("payroll question")
        
        expected_result = "Payroll policy details\nExpense reimbursement process"
        assert result == expected_result
        mock_load_rag.assert_called_once()
    
    @patch('agents.finance_agent.load_finance_rag_chain')
    def test_internal_finance_search_exception_handling(self, mock_load_rag):
        """Test internal finance search handles exceptions"""
        mock_load_rag.side_effect = Exception("RAG chain loading failed")
        
        result = internal_finance_search.func("test query")
        assert result == ""


class TestWebSearch:
    """Test cases for the web_search tool"""
    
    @patch('agents.finance_agent.tavily_search')
    def test_web_search_calls_tavily(self, mock_tavily):
        """Test web search calls Tavily search"""
        mock_tavily.return_value = "Web search results"
        
        result = web_search.func("tax rates")
        
        assert result == "Web search results"
        mock_tavily.assert_called_once_with("tax rates")


class TestFinanceAgent:
    """Test cases for the finance_agent function"""
    
    @patch('agents.finance_agent.create_agent')
    @patch('agents.finance_agent.get_llm')
    def test_finance_agent_dict_input(self, mock_get_llm, mock_create_agent):
        """Test finance agent with dictionary input"""
        # Mock LLM
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        # Mock agent and its response
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        
        # Mock agent response with messages
        mock_ai_message = Mock()
        mock_ai_message.type = "ai"
        mock_ai_message.content = "Finance support response"
        mock_result = {"messages": [mock_ai_message]}
        mock_agent.invoke.return_value = mock_result
        
        state = {"query": "What is the reimbursement policy?"}
        result = finance_agent(state)
        
        assert result["query"] == "What is the reimbursement policy?"
        assert result["route"] == "FINANCE"
        assert result["response"] == "Finance support response"
    
    @patch('agents.finance_agent.create_agent')
    @patch('agents.finance_agent.get_llm')
    def test_finance_agent_string_input(self, mock_get_llm, mock_create_agent):
        """Test finance agent with string input"""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        
        mock_ai_message = Mock()
        mock_ai_message.type = "ai"
        mock_ai_message.content = "Payroll information"
        mock_result = {"messages": [mock_ai_message]}
        mock_agent.invoke.return_value = mock_result
        
        query_string = "How is my salary calculated?"
        result = finance_agent(query_string)
        
        assert result["query"] == "How is my salary calculated?"
        assert result["route"] == "FINANCE"
        assert result["response"] == "Payroll information"
    
    @patch('agents.finance_agent.create_agent')
    @patch('agents.finance_agent.get_llm')
    def test_finance_agent_system_prompt_content(self, mock_get_llm, mock_create_agent):
        """Test finance agent system prompt contains required elements"""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        
        mock_ai_message = Mock()
        mock_ai_message.type = "ai"
        mock_ai_message.content = "Response"
        mock_result = {"messages": [mock_ai_message]}
        mock_agent.invoke.return_value = mock_result
        
        state = {"query": "Test finance question"}
        finance_agent(state)
        
        # Get the system prompt from create_agent call
        call_args = mock_create_agent.call_args
        system_prompt = call_args[1]["system_prompt"] if "system_prompt" in call_args[1] else call_args[0][2]
        
        # Check system prompt contains mandatory process steps
        assert "STEP 1: ALWAYS start by using internal_finance_search" in system_prompt
        assert "STEP 2: Review the internal search results" in system_prompt
        assert "I'm a Finance Support Agent" in system_prompt
    
    @patch('agents.finance_agent.create_agent')
    @patch('agents.finance_agent.get_llm')
    def test_finance_agent_tools_provided(self, mock_get_llm, mock_create_agent):
        """Test finance agent is created with correct tools"""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        
        mock_ai_message = Mock()
        mock_ai_message.type = "ai"
        mock_ai_message.content = "Response"
        mock_result = {"messages": [mock_ai_message]}
        mock_agent.invoke.return_value = mock_result
        
        state = {"query": "Test question"}
        finance_agent(state)
        
        # Check tools provided to create_agent
        call_args = mock_create_agent.call_args
        # Tools are passed as keyword argument
        tools = call_args[1]["tools"] if "tools" in call_args[1] else call_args[0][1]
        
        assert len(tools) == 2
        # Tools should include internal_finance_search and web_search
        tool_names = [tool.name for tool in tools]
        assert "internal_finance_search" in tool_names
        assert "web_search" in tool_names


class TestFinanceAgentIntegration:
    """Integration tests for finance agent functionality"""
    
    @patch('agents.finance_agent.create_agent')
    @patch('agents.finance_agent.get_llm')
    def test_finance_agent_typical_workflow(self, mock_get_llm, mock_create_agent):
        """Test typical finance agent workflow"""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        
        mock_ai_message = Mock()
        mock_ai_message.type = "ai"
        mock_ai_message.content = "Based on internal finance policies, here's the reimbursement process..."
        mock_result = {"messages": [mock_ai_message]}
        mock_agent.invoke.return_value = mock_result
        
        state = {"query": "How do I submit expense reports?"}
        result = finance_agent(state)
        
        assert result["query"] == "How do I submit expense reports?"
        assert result["route"] == "FINANCE"
        assert "reimbursement" in result["response"]
    
    @patch('agents.finance_agent.create_agent')
    @patch('agents.finance_agent.get_llm')  
    def test_finance_agent_various_queries(self, mock_get_llm, mock_create_agent):
        """Test finance agent with various finance-related queries"""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        
        test_queries = [
            "Payroll processing questions",
            "Budget approval requests",
            "Tax rate information",
            "Invoice processing help",
            "Expense policy clarification"
        ]
        
        for query in test_queries:
            mock_ai_message = Mock()
            mock_ai_message.type = "ai"
            mock_ai_message.content = f"Finance support response for {query}"
            mock_result = {"messages": [mock_ai_message]}
            mock_agent.invoke.return_value = mock_result
            
            state = {"query": query}
            result = finance_agent(state)
            
            assert result["query"] == query
            assert result["route"] == "FINANCE"
            assert query in result["response"] or "Finance support" in result["response"]


if __name__ == "__main__":
    pytest.main([__file__])
