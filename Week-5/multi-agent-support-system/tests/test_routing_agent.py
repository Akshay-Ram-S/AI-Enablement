import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.routing_agent import supervisor_agent, dynamic_routing_agent


class TestSupervisorAgent:
    """Test cases for the supervisor_agent function"""
    
    @patch('agents.routing_agent.get_llm')
    def test_supervisor_agent_it_query(self, mock_get_llm):
        """Test supervisor agent correctly routes IT-related queries"""
        # Mock LLM response
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "IT"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        # Test IT query
        state = {"query": "How do I set up VPN on my laptop?"}
        result = supervisor_agent(state)
        
        assert result["query"] == "How do I set up VPN on my laptop?"
        assert result["route"] == "IT"
        assert result["response"] == ""
        mock_llm.invoke.assert_called_once()
    
    @patch('agents.routing_agent.get_llm')
    def test_supervisor_agent_finance_query(self, mock_get_llm):
        """Test supervisor agent correctly routes Finance-related queries"""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "FINANCE"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        state = {"query": "What is the reimbursement policy for travel expenses?"}
        result = supervisor_agent(state)
        
        assert result["query"] == "What is the reimbursement policy for travel expenses?"
        assert result["route"] == "FINANCE"
        assert result["response"] == ""
    
    @patch('agents.routing_agent.get_llm')
    def test_supervisor_agent_irrelevant_query_defaults_to_it(self, mock_get_llm):
        """Test supervisor agent defaults to IT for irrelevant queries"""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "IRRELEVANT"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        state = {"query": "What's the weather today?"}
        result = supervisor_agent(state)
        
        assert result["query"] == "What's the weather today?"
        assert result["route"] == "IT"  # Should default to IT for invalid routes
        assert result["response"] == ""
    
    @patch('agents.routing_agent.get_llm')
    def test_supervisor_agent_string_input(self, mock_get_llm):
        """Test supervisor agent handles string input instead of dict"""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "IT"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        # Test with string input
        query_string = "My computer won't start"
        result = supervisor_agent(query_string)
        
        assert result["query"] == "My computer won't start"
        assert result["route"] == "IT"
        assert result["response"] == ""
    
    @patch('agents.routing_agent.get_llm')
    def test_supervisor_agent_llm_exception_handling(self, mock_get_llm):
        """Test supervisor agent handles LLM exceptions gracefully"""
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("LLM connection failed")
        mock_get_llm.return_value = mock_llm
        
        state = {"query": "Test query"}
        result = supervisor_agent(state)
        
        assert result["query"] == "Test query"
        assert result["route"] == "IT"  # Should default to IT on error
        assert "Error in routing" in result["response"]
    
    @patch('agents.routing_agent.get_llm')
    def test_supervisor_agent_lowercase_response_handling(self, mock_get_llm):
        """Test supervisor agent handles lowercase LLM responses"""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "finance"  # lowercase
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        state = {"query": "Payroll question"}
        result = supervisor_agent(state)
        
        assert result["route"] == "FINANCE"  # Should be converted to uppercase
    
    @patch('agents.routing_agent.get_llm')
    def test_supervisor_agent_whitespace_handling(self, mock_get_llm):
        """Test supervisor agent handles responses with whitespace"""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "  IT  "  # with whitespace
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        state = {"query": "Network issue"}
        result = supervisor_agent(state)
        
        assert result["route"] == "IT"  # Should strip whitespace
    
    @patch('agents.routing_agent.get_llm')
    def test_supervisor_agent_unexpected_response(self, mock_get_llm):
        """Test supervisor agent handles unexpected LLM responses"""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "UNKNOWN_CATEGORY"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        state = {"query": "Random query"}
        result = supervisor_agent(state)
        
        assert result["route"] == "IT"  # Should default to IT for unknown categories
    
    def test_supervisor_agent_system_prompt_content(self):
        """Test that system prompt contains expected classification categories"""
        with patch('agents.routing_agent.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = "IT"
            mock_llm.invoke.return_value = mock_response
            mock_get_llm.return_value = mock_llm
            
            state = {"query": "Test query"}
            supervisor_agent(state)
            
            # Get the system prompt that was passed to LLM
            call_args = mock_llm.invoke.call_args[0][0]
            
            # Check that prompt contains expected categories
            assert "IT-related topics include:" in call_args
            assert "Finance-related topics include:" in call_args
            assert "NON-RELEVANT topics include:" in call_args
            assert "VPN setup" in call_args
            assert "Payroll" in call_args


class TestDynamicRoutingAgent:
    """Test cases for the dynamic_routing_agent function"""
    
    @patch('agents.routing_agent.supervisor_agent')
    def test_dynamic_routing_agent_calls_supervisor(self, mock_supervisor):
        """Test dynamic_routing_agent is an alias for supervisor_agent"""
        expected_result = {"query": "test", "route": "IT", "response": ""}
        mock_supervisor.return_value = expected_result
        
        state = {"query": "test query"}
        result = dynamic_routing_agent(state)
        
        assert result == expected_result
        mock_supervisor.assert_called_once_with(state)


class TestRoutingAgentIntegration:
    """Integration tests for routing agent functionality"""
    
    @patch('agents.routing_agent.get_llm')
    def test_it_queries_routing(self, mock_get_llm):
        """Test various IT-related queries are routed correctly"""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "IT"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        it_queries = [
            "How to reset my password?",
            "VPN connection issues",
            "Software installation help",
            "My laptop is not working",
            "Network connectivity problems",
            "Security policy questions"
        ]
        
        for query in it_queries:
            result = supervisor_agent({"query": query})
            assert result["route"] == "IT", f"Query '{query}' should route to IT"
    
    @patch('agents.routing_agent.get_llm')
    def test_finance_queries_routing(self, mock_get_llm):
        """Test various Finance-related queries are routed correctly"""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "FINANCE"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        finance_queries = [
            "What is my salary?",
            "Reimbursement process",
            "Budget approval needed",
            "Invoice processing help",
            "Tax rate information",
            "Expense policy clarification"
        ]
        
        for query in finance_queries:
            result = supervisor_agent({"query": query})
            assert result["route"] == "FINANCE", f"Query '{query}' should route to FINANCE"


if __name__ == "__main__":
    pytest.main([__file__])
