import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from graph.workflow import (
    route_to_agent, 
    irrelevant_handler, 
    create_supervisor_workflow, 
    create_dynamic_workflow,
    app
)


class TestRouteToAgent:
    """Test cases for the route_to_agent function"""
    
    def test_route_to_agent_finance_route(self):
        """Test routing to finance agent"""
        state = {"route": "FINANCE", "query": "Payroll question"}
        result = route_to_agent(state)
        assert result == "finance_agent"
    
    def test_route_to_agent_it_route(self):
        """Test routing to IT agent"""
        state = {"route": "IT", "query": "Network issue"}
        result = route_to_agent(state)
        assert result == "it_agent"
    
    def test_route_to_agent_irrelevant_route(self):
        """Test routing to irrelevant handler"""
        state = {"route": "IRRELEVANT", "query": "Weather question"}
        result = route_to_agent(state)
        assert result == "irrelevant_handler"
    
    def test_route_to_agent_unknown_route_defaults_to_it(self):
        """Test unknown routes default to IT agent"""
        state = {"route": "UNKNOWN", "query": "Some question"}
        result = route_to_agent(state)
        assert result == "it_agent"
    
    def test_route_to_agent_missing_route_defaults_to_it(self):
        """Test missing route defaults to IT agent"""
        state = {"query": "Some question"}
        result = route_to_agent(state)
        assert result == "it_agent"
    
    def test_route_to_agent_none_route_defaults_to_it(self):
        """Test None route defaults to IT agent"""
        state = {"route": None, "query": "Some question"}
        result = route_to_agent(state)
        assert result == "it_agent"
    
    def test_route_to_agent_empty_string_route_defaults_to_it(self):
        """Test empty string route defaults to IT agent"""
        state = {"route": "", "query": "Some question"}
        result = route_to_agent(state)
        assert result == "it_agent"


class TestIrrelevantHandler:
    """Test cases for the irrelevant_handler function"""
    
    def test_irrelevant_handler_returns_proper_response(self):
        """Test irrelevant handler returns appropriate response"""
        state = {"query": "What's the weather like today?"}
        result = irrelevant_handler(state)
        
        expected_response = ("I'm a corporate support system that handles IT and Finance-related queries only. "
                           "For questions about weather, sports, cooking, or other non-business topics, "
                           "please use appropriate external resources or contact the relevant department.")
        
        assert result["query"] == "What's the weather like today?"
        assert result["route"] == "IRRELEVANT"
        assert result["response"] == expected_response
    
    def test_irrelevant_handler_with_complex_query(self):
        """Test irrelevant handler with complex non-business query"""
        state = {"query": "Can you help me cook dinner and tell me about sports scores?"}
        result = irrelevant_handler(state)
        
        assert result["query"] == "Can you help me cook dinner and tell me about sports scores?"
        assert result["route"] == "IRRELEVANT"
        assert "corporate support system" in result["response"]
        assert "IT and Finance-related queries only" in result["response"]
    
    def test_irrelevant_handler_preserves_original_query(self):
        """Test irrelevant handler preserves the original query exactly"""
        original_query = "What are some good movie recommendations?"
        state = {"query": original_query}
        result = irrelevant_handler(state)
        
        assert result["query"] == original_query
        assert result["route"] == "IRRELEVANT"


class TestCreateSupervisorWorkflow:
    """Test cases for the create_supervisor_workflow function"""
    
    @patch('graph.workflow.supervisor_agent')
    @patch('graph.workflow.it_agent')
    @patch('graph.workflow.finance_agent')
    @patch('graph.workflow.StateGraph')
    def test_create_supervisor_workflow_structure(self, mock_state_graph, 
                                                mock_finance_agent, mock_it_agent, 
                                                mock_supervisor_agent):
        """Test that workflow is created with correct structure"""
        # Mock the StateGraph and its methods
        mock_graph_instance = Mock()
        mock_state_graph.return_value = mock_graph_instance
        mock_compiled_app = Mock()
        mock_graph_instance.compile.return_value = mock_compiled_app
        
        # Call the function
        result = create_supervisor_workflow()
        
        # Verify StateGraph was initialized with dict
        mock_state_graph.assert_called_once_with(dict)
        
        # Verify nodes were added
        expected_nodes = [
            ("supervisor", mock_supervisor_agent),
            ("it_agent", mock_it_agent),
            ("finance_agent", mock_finance_agent),
            ("irrelevant_handler", irrelevant_handler)
        ]
        
        for node_name, node_func in expected_nodes:
            mock_graph_instance.add_node.assert_any_call(node_name, node_func)
        
        # Verify entry point was set
        mock_graph_instance.set_entry_point.assert_called_once_with("supervisor")
        
        # Verify finish points were set
        finish_point_calls = mock_graph_instance.set_finish_point.call_args_list
        finish_points = [call[0][0] for call in finish_point_calls]
        expected_finish_points = ["it_agent", "finance_agent", "irrelevant_handler"]
        
        for point in expected_finish_points:
            assert point in finish_points
        
        # Verify conditional edges were added
        mock_graph_instance.add_conditional_edges.assert_called_once()
        
        # Verify compile was called and result returned
        mock_graph_instance.compile.assert_called_once()
        assert result == mock_compiled_app
    
    @patch('graph.workflow.StateGraph')
    def test_create_supervisor_workflow_conditional_edges_mapping(self, mock_state_graph):
        """Test conditional edges mapping is correct"""
        mock_graph_instance = Mock()
        mock_state_graph.return_value = mock_graph_instance
        mock_graph_instance.compile.return_value = Mock()
        
        create_supervisor_workflow()
        
        # Get the call arguments for add_conditional_edges
        call_args = mock_graph_instance.add_conditional_edges.call_args
        
        # Verify the call structure
        assert call_args[0][0] == "supervisor"  # source node
        assert call_args[0][1] == route_to_agent  # routing function
        
        # Verify the mapping
        expected_mapping = {
            "it_agent": "it_agent",
            "finance_agent": "finance_agent", 
            "irrelevant_handler": "irrelevant_handler"
        }
        assert call_args[0][2] == expected_mapping


class TestCreateDynamicWorkflow:
    """Test cases for the create_dynamic_workflow function"""
    
    @patch('graph.workflow.create_supervisor_workflow')
    def test_create_dynamic_workflow_calls_supervisor(self, mock_create_supervisor):
        """Test create_dynamic_workflow is an alias for create_supervisor_workflow"""
        expected_app = Mock()
        mock_create_supervisor.return_value = expected_app
        
        result = create_dynamic_workflow()
        
        mock_create_supervisor.assert_called_once()
        assert result == expected_app


class TestWorkflowIntegration:
    """Integration tests for workflow functionality"""
    
    def test_workflow_routing_logic_integration(self):
        """Test the complete routing logic with different states"""
        test_cases = [
            ({"route": "FINANCE", "query": "payroll"}, "finance_agent"),
            ({"route": "IT", "query": "network"}, "it_agent"),
            ({"route": "IRRELEVANT", "query": "weather"}, "irrelevant_handler"),
            ({"route": "UNKNOWN", "query": "test"}, "it_agent"),
            ({"query": "test"}, "it_agent"),  # missing route
        ]
        
        for state, expected_route in test_cases:
            result = route_to_agent(state)
            assert result == expected_route, f"State {state} should route to {expected_route}"
    
    def test_irrelevant_handler_response_consistency(self):
        """Test irrelevant handler provides consistent responses"""
        queries = [
            "What's the weather?",
            "Recipe for cookies",
            "Sports scores today",
            "Movie recommendations",
            "Travel destinations"
        ]
        
        for query in queries:
            state = {"query": query}
            result = irrelevant_handler(state)
            
            assert result["route"] == "IRRELEVANT"
            assert result["query"] == query
            assert "corporate support system" in result["response"]
            assert "IT and Finance-related queries only" in result["response"]
    
    @patch('graph.workflow.StateGraph')
    def test_workflow_creation_error_handling(self, mock_state_graph):
        """Test workflow creation handles errors gracefully"""
        # Mock StateGraph to raise an exception
        mock_state_graph.side_effect = Exception("StateGraph creation failed")
        
        with pytest.raises(Exception) as exc_info:
            create_supervisor_workflow()
        
        assert "StateGraph creation failed" in str(exc_info.value)


class TestWorkflowApp:
    """Test cases for the compiled workflow app"""
    
    def test_app_exists(self):
        """Test that the app is created and available"""
        assert app is not None
        # App should be a compiled StateGraph
        assert hasattr(app, 'invoke') or hasattr(app, '__call__')


class TestWorkflowEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_route_to_agent_with_none_state(self):
        """Test route_to_agent handles None state gracefully"""
        # This might raise an exception, which is acceptable behavior
        try:
            result = route_to_agent(None)
            assert result == "it_agent"  # Should default to IT
        except (AttributeError, TypeError):
            # It's acceptable if this raises an exception with None input
            pass
    
    def test_irrelevant_handler_with_missing_query(self):
        """Test irrelevant handler with missing query field"""
        state = {}  # No query field
        
        # This should handle gracefully or raise a clear error
        try:
            result = irrelevant_handler(state)
            # If it handles gracefully, query should be None or empty
            assert "query" in result
        except KeyError:
            # Acceptable if it expects query to be present
            pass
    
    def test_route_to_agent_case_sensitivity(self):
        """Test route_to_agent handles different case variations"""
        test_cases = [
            {"route": "finance", "expected": "it_agent"},  # lowercase should default to IT
            {"route": "Finance", "expected": "it_agent"},  # mixed case should default to IT
            {"route": "FINANCE", "expected": "finance_agent"},  # correct case
            {"route": "it", "expected": "it_agent"},  # lowercase should default to IT (not matching "IT")
        ]
        
        for case in test_cases:
            state = {"route": case["route"], "query": "test"}
            result = route_to_agent(state)
            assert result == case["expected"], f"Route '{case['route']}' should map to '{case['expected']}'"


if __name__ == "__main__":
    pytest.main([__file__])
