import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.tavily_tool import tavily_search


class TestTavilySearch:
    """Major test cases for the tavily_search function"""
    
    @patch('tools.tavily_tool.TavilyClient')
    def test_tavily_search_success(self, mock_tavily_client_class):
        """Test successful Tavily search"""
        mock_client = Mock()
        mock_tavily_client_class.return_value = mock_client
        
        mock_result = {
            "results": [
                {"title": "Test Result 1", "content": "Test content 1"},
                {"title": "Test Result 2", "content": "Test content 2"}
            ],
            "answer": "Test answer from Tavily"
        }
        mock_client.search.return_value = mock_result
        
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test_api_key"}):
            result = tavily_search("test query")
        
        # Verify client was created with API key
        mock_tavily_client_class.assert_called_once_with(api_key="test_api_key")
        
        # Verify search was called with correct parameters
        mock_client.search.assert_called_once_with(
            query="test query",
            max_results=5,
            include_answer=True
        )
        
        # Result should be string representation of the mock result
        assert str(mock_result) in result
    
    @patch('tools.tavily_tool.TavilyClient')
    def test_tavily_search_missing_api_key(self, mock_tavily_client_class):
        """Test Tavily search with missing API key"""
        mock_tavily_client_class.side_effect = KeyError("TAVILY_API_KEY")
        
        # Remove API key from environment if it exists
        with patch.dict(os.environ, {}, clear=True):
            result = tavily_search("test query")
        
        assert "Tavily search unavailable:" in result
        assert "TAVILY_API_KEY" in result
    
    @patch('tools.tavily_tool.TavilyClient')
    def test_tavily_search_client_exception(self, mock_tavily_client_class):
        """Test Tavily search with client exception"""
        mock_client = Mock()
        mock_tavily_client_class.return_value = mock_client
        mock_client.search.side_effect = Exception("API connection failed")
        
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test_api_key"}):
            result = tavily_search("test query")
        
        assert "Tavily search unavailable:" in result
        assert "API connection failed" in result
    
    @patch('tools.tavily_tool.TavilyClient')
    def test_tavily_search_different_queries(self, mock_tavily_client_class):
        """Test Tavily search with different query types"""
        mock_client = Mock()
        mock_tavily_client_class.return_value = mock_client
        mock_client.search.return_value = {"answer": "Test response"}
        
        test_queries = [
            "How to reset password",
            "Network troubleshooting",
            "Security best practices",
            "Software installation guide"
        ]
        
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test_api_key"}):
            for query in test_queries:
                result = tavily_search(query)
                
                # Verify each query was processed
                assert "Test response" in result
                
        # Verify search was called for each query
        assert mock_client.search.call_count == len(test_queries)
    
    @patch('tools.tavily_tool.TavilyClient')
    def test_tavily_search_empty_result(self, mock_tavily_client_class):
        """Test Tavily search with empty result"""
        mock_client = Mock()
        mock_tavily_client_class.return_value = mock_client
        mock_client.search.return_value = {}
        
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test_api_key"}):
            result = tavily_search("no results query")
        
        assert result == "{}"


if __name__ == "__main__":
    pytest.main([__file__])
