import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.it_agent import _fetch_docs_with_fallback, internal_it_search, web_search, it_agent


class TestFetchDocsWithFallback:
    """Test cases for the _fetch_docs_with_fallback utility function"""
    
    def test_fetch_docs_with_get_relevant_documents(self):
        """Test fetching docs using get_relevant_documents method"""
        mock_retriever = Mock()
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.page_content = "IT policy content"
        mock_retriever.get_relevant_documents.return_value = [mock_doc]
        
        query = "VPN setup"
        result = _fetch_docs_with_fallback(mock_retriever, mock_db, query)
        
        assert result == [mock_doc]
        mock_retriever.get_relevant_documents.assert_called_once_with(query)
        mock_db.similarity_search.assert_not_called()
    
    def test_fetch_docs_with_retrieve_method(self):
        """Test fetching docs using retrieve method when get_relevant_documents unavailable"""
        mock_retriever = Mock(spec=[])  # No get_relevant_documents method
        mock_retriever.retrieve = Mock()
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.page_content = "IT content"
        mock_retriever.retrieve.return_value = [mock_doc]
        
        query = "network issue"
        result = _fetch_docs_with_fallback(mock_retriever, mock_db, query)
        
        assert result == [mock_doc]
        mock_retriever.retrieve.assert_called_once_with(query)
    
    def test_fetch_docs_with_similarity_search(self):
        """Test fetching docs using similarity_search as fallback"""
        mock_retriever = Mock(spec=[])  # No get_relevant_documents or retrieve
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.page_content = "Similar IT content"
        mock_db.similarity_search.return_value = [mock_doc]
        
        query = "password reset"
        result = _fetch_docs_with_fallback(mock_retriever, mock_db, query)
        
        assert result == [mock_doc]
        mock_db.similarity_search.assert_called_once_with(query, k=4)
    
    def test_fetch_docs_exception_handling(self):
        """Test exception handling in _fetch_docs_with_fallback"""
        mock_retriever = Mock()
        mock_retriever.get_relevant_documents.side_effect = Exception("Database error")
        mock_db = Mock()
        
        query = "test query"
        result = _fetch_docs_with_fallback(mock_retriever, mock_db, query)
        
        assert result == []
    
    def test_fetch_docs_no_available_methods(self):
        """Test when no retrieval methods are available"""
        mock_retriever = Mock(spec=[])  # No methods
        mock_db = Mock(spec=[])  # No similarity_search
        
        query = "test query"
        result = _fetch_docs_with_fallback(mock_retriever, mock_db, query)
        
        assert result == []


class TestInternalItSearch:
    """Test cases for the internal_it_search tool"""
    
    @patch('agents.it_agent.load_it_rag_chain')
    @patch('agents.it_agent._fetch_docs_with_fallback')
    def test_internal_it_search_success(self, mock_fetch_docs, mock_load_rag):
        """Test successful internal IT search"""
        # Mock RAG chain loading
        mock_retriever = Mock()
        mock_db = Mock()
        mock_chain = Mock()
        mock_load_rag.return_value = (mock_retriever, mock_db, mock_chain)
        
        # Mock document fetching
        mock_doc1 = Mock()
        mock_doc1.page_content = "VPN setup instructions"
        mock_doc2 = Mock()
        mock_doc2.page_content = "Network configuration details"
        mock_fetch_docs.return_value = [mock_doc1, mock_doc2]
        
        query = "VPN setup help"
        result = internal_it_search.func(query)
        
        expected_result = "VPN setup instructions\nNetwork configuration details"
        assert result == expected_result
        mock_load_rag.assert_called_once()
        mock_fetch_docs.assert_called_once_with(mock_retriever, mock_db, query)
    
    @patch('agents.it_agent.load_it_rag_chain')
    @patch('agents.it_agent._fetch_docs_with_fallback')
    def test_internal_it_search_no_docs(self, mock_fetch_docs, mock_load_rag):
        """Test internal IT search when no documents found"""
        mock_retriever = Mock()
        mock_db = Mock()
        mock_chain = Mock()
        mock_load_rag.return_value = (mock_retriever, mock_db, mock_chain)
        mock_fetch_docs.return_value = []
        
        query = "unknown topic"
        result = internal_it_search.func(query)
        
        assert result == ""
    
    @patch('agents.it_agent.load_it_rag_chain')
    def test_internal_it_search_exception_handling(self, mock_load_rag):
        """Test internal IT search handles exceptions"""
        mock_load_rag.side_effect = Exception("RAG chain loading failed")
        
        query = "test query"
        result = internal_it_search.func(query)
        
        assert result == ""
    
    @patch('agents.it_agent.load_it_rag_chain')
    @patch('agents.it_agent._fetch_docs_with_fallback')
    def test_internal_it_search_single_doc(self, mock_fetch_docs, mock_load_rag):
        """Test internal IT search with single document"""
        mock_retriever = Mock()
        mock_db = Mock()
        mock_chain = Mock()
        mock_load_rag.return_value = (mock_retriever, mock_db, mock_chain)
        
        mock_doc = Mock()
        mock_doc.page_content = "Single IT policy document"
        mock_fetch_docs.return_value = [mock_doc]
        
        query = "policy question"
        result = internal_it_search.func(query)
        
        assert result == "Single IT policy document"


class TestWebSearch:
    """Test cases for the web_search tool"""
    
    @patch('agents.it_agent.tavily_search')
    def test_web_search_calls_tavily(self, mock_tavily):
        """Test web search calls Tavily search"""
        mock_tavily.return_value = "Web search results"
        
        query = "latest security updates"
        result = web_search.func(query)
        
        assert result == "Web search results"
        mock_tavily.assert_called_once_with(query)
    
    @patch('agents.it_agent.tavily_search')
    def test_web_search_empty_result(self, mock_tavily):
        """Test web search with empty result"""
        mock_tavily.return_value = ""
        
        query = "no results query"
        result = web_search.func(query)
        
        assert result == ""
    
    @patch('agents.it_agent.tavily_search')
    def test_web_search_exception_propagation(self, mock_tavily):
        """Test web search exception propagation"""
        mock_tavily.side_effect = Exception("Tavily API error")
        
        query = "test query"
        with pytest.raises(Exception) as exc_info:
            web_search.func(query)
        
        assert "Tavily API error" in str(exc_info.value)


class TestItAgent:
    """Test cases for the it_agent function"""
    
    @patch('agents.it_agent.create_agent')
    @patch('agents.it_agent.get_llm')
    def test_it_agent_dict_input(self, mock_get_llm, mock_create_agent):
        """Test IT agent with dictionary input"""
        # Mock LLM
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        # Mock agent and its response
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        
        # Mock agent response with messages
        mock_ai_message = Mock()
        mock_ai_message.type = "ai"
        mock_ai_message.content = "IT support response"
        mock_result = {"messages": [mock_ai_message]}
        mock_agent.invoke.return_value = mock_result
        
        state = {"query": "How to reset password?"}
        result = it_agent(state)
        
        assert result["query"] == "How to reset password?"
        assert result["route"] == "IT"
        assert result["response"] == "IT support response"
        
        # Verify agent creation
        mock_create_agent.assert_called_once()
        call_args = mock_create_agent.call_args
        assert call_args[0][0] == mock_llm  # LLM parameter
        # Tools are passed as keyword argument
        tools = call_args[1]["tools"] if "tools" in call_args[1] else call_args[0][1]
        assert len(tools) == 2  # Tools list should have internal_it_search and web_search
        assert "system_prompt" in call_args[1] or len(call_args[0]) > 2  # System prompt provided
    
    @patch('agents.it_agent.create_agent')
    @patch('agents.it_agent.get_llm')
    def test_it_agent_string_input(self, mock_get_llm, mock_create_agent):
        """Test IT agent with string input"""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        
        mock_ai_message = Mock()
        mock_ai_message.type = "ai"
        mock_ai_message.content = "String input response"
        mock_result = {"messages": [mock_ai_message]}
        mock_agent.invoke.return_value = mock_result
        
        query_string = "Network connectivity issues"
        result = it_agent(query_string)
        
        assert result["query"] == "Network connectivity issues"
        assert result["route"] == "IT"
        assert result["response"] == "String input response"
    
    @patch('agents.it_agent.create_agent')
    @patch('agents.it_agent.get_llm')
    def test_it_agent_system_prompt_content(self, mock_get_llm, mock_create_agent):
        """Test IT agent system prompt contains required elements"""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        
        mock_ai_message = Mock()
        mock_ai_message.type = "ai"
        mock_ai_message.content = "Response"
        mock_result = {"messages": [mock_ai_message]}
        mock_agent.invoke.return_value = mock_result
        
        state = {"query": "Test IT question"}
        it_agent(state)
        
        # Get the system prompt from create_agent call
        call_args = mock_create_agent.call_args
        system_prompt = call_args[1]["system_prompt"] if "system_prompt" in call_args[1] else call_args[0][2]
        
        # Check system prompt contains mandatory process steps
        assert "STEP 1: ALWAYS start by using internal_it_search" in system_prompt
        assert "STEP 2: Review the internal search results" in system_prompt
        assert "STEP 3: If internal documents provide sufficient information" in system_prompt
        assert "STEP 4: If internal documents are incomplete" in system_prompt
        assert "STEP 5: Combine internal and external information" in system_prompt
        assert "I'm an IT Support Agent" in system_prompt
    
    @patch('agents.it_agent.create_agent')
    @patch('agents.it_agent.get_llm')
    def test_it_agent_tools_provided(self, mock_get_llm, mock_create_agent):
        """Test IT agent is created with correct tools"""
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
        it_agent(state)
        
        # Check tools provided to create_agent
        call_args = mock_create_agent.call_args
        # Tools are passed as keyword argument
        tools = call_args[1]["tools"] if "tools" in call_args[1] else call_args[0][1]
        
        assert len(tools) == 2
        # Tools should include internal_it_search and web_search
        tool_names = [tool.name for tool in tools]
        assert "internal_it_search" in tool_names
        assert "web_search" in tool_names
    
    @patch('agents.it_agent.create_agent')
    @patch('agents.it_agent.get_llm')
    def test_it_agent_multiple_ai_messages(self, mock_get_llm, mock_create_agent):
        """Test IT agent handles multiple AI messages correctly"""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        
        # Multiple messages, should pick the last AI message
        mock_ai_message_1 = Mock()
        mock_ai_message_1.type = "ai"
        mock_ai_message_1.content = "First response"
        
        mock_human_message = Mock()
        mock_human_message.type = "human"
        mock_human_message.content = "Human message"
        
        mock_ai_message_2 = Mock()
        mock_ai_message_2.type = "ai"
        mock_ai_message_2.content = "Final response"
        
        mock_result = {"messages": [mock_ai_message_1, mock_human_message, mock_ai_message_2]}
        mock_agent.invoke.return_value = mock_result
        
        state = {"query": "Multiple messages test"}
        result = it_agent(state)
        
        # Should use the last AI message
        assert result["response"] == "Final response"
    
    @patch('agents.it_agent.create_agent')
    @patch('agents.it_agent.get_llm')
    def test_it_agent_no_ai_messages(self, mock_get_llm, mock_create_agent):
        """Test IT agent handles case with no AI messages"""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        
        mock_human_message = Mock()
        mock_human_message.type = "human"
        mock_human_message.content = "Human message"
        
        mock_result = {"messages": [mock_human_message]}
        mock_agent.invoke.return_value = mock_result
        
        state = {"query": "No AI messages test"}
        
        # Should raise StopIteration when no AI messages found
        with pytest.raises(StopIteration):
            it_agent(state)


class TestItAgentIntegration:
    """Integration tests for IT agent functionality"""
    
    @patch('agents.it_agent.create_agent')
    @patch('agents.it_agent.get_llm')
    def test_it_agent_typical_workflow(self, mock_get_llm, mock_create_agent):
        """Test typical IT agent workflow"""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        
        mock_ai_message = Mock()
        mock_ai_message.type = "ai"
        mock_ai_message.content = "Based on internal IT policies and web search, here's how to reset your password..."
        mock_result = {"messages": [mock_ai_message]}
        mock_agent.invoke.return_value = mock_result
        
        state = {"query": "How do I reset my company password?"}
        result = it_agent(state)
        
        assert result["query"] == "How do I reset my company password?"
        assert result["route"] == "IT"
        assert "password" in result["response"]
        
        # Verify agent was invoked with proper input
        mock_agent.invoke.assert_called_once()
        invoke_args = mock_agent.invoke.call_args[0][0]
        assert "Please help me with: How do I reset my company password?" in invoke_args["input"]
    
    @patch('agents.it_agent.create_agent')
    @patch('agents.it_agent.get_llm')  
    def test_it_agent_various_it_queries(self, mock_get_llm, mock_create_agent):
        """Test IT agent with various IT-related queries"""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        
        test_queries = [
            "VPN connection troubleshooting",
            "Software installation help",
            "Network printer setup",
            "Security policy questions",
            "Hardware replacement request",
            "Email configuration issues"
        ]
        
        for query in test_queries:
            mock_ai_message = Mock()
            mock_ai_message.type = "ai"
            mock_ai_message.content = f"IT support response for {query}"
            mock_result = {"messages": [mock_ai_message]}
            mock_agent.invoke.return_value = mock_result
            
            state = {"query": query}
            result = it_agent(state)
            
            assert result["query"] == query
            assert result["route"] == "IT"
            assert query in result["response"] or "IT support" in result["response"]


class TestItAgentTools:
    """Test the tool functions work correctly as LangChain tools"""
    
    def test_internal_it_search_tool_decorator(self):
        """Test internal_it_search has correct tool decorator"""
        assert hasattr(internal_it_search, 'name')
        assert internal_it_search.name == "internal_it_search"
        assert hasattr(internal_it_search, 'description')
        assert "internal IT company documents" in internal_it_search.description
    
    def test_web_search_tool_decorator(self):
        """Test web_search has correct tool decorator"""
        assert hasattr(web_search, 'name')
        assert web_search.name == "web_search"
        assert hasattr(web_search, 'description')
        assert "Search the web" in web_search.description


if __name__ == "__main__":
    pytest.main([__file__])
