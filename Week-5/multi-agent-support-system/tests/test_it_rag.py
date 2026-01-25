import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rag.it_rag import _format_docs, _web_search, load_it_rag_chain


class TestFormatDocs:
    """Test cases for the _format_docs utility function"""
    
    def test_format_docs_with_documents(self):
        """Test formatting multiple documents"""
        mock_doc1 = Mock()
        mock_doc1.page_content = "First document content"
        mock_doc2 = Mock()
        mock_doc2.page_content = "Second document content"
        mock_doc3 = Mock()
        mock_doc3.page_content = "Third document content"
        
        docs = [mock_doc1, mock_doc2, mock_doc3]
        result = _format_docs(docs)
        
        expected = "First document content\n\nSecond document content\n\nThird document content"
        assert result == expected
    
    def test_format_docs_single_document(self):
        """Test formatting single document"""
        mock_doc = Mock()
        mock_doc.page_content = "Single document content"
        
        result = _format_docs([mock_doc])
        assert result == "Single document content"
    
    def test_format_docs_empty_list(self):
        """Test formatting empty document list"""
        result = _format_docs([])
        assert result == ""
    
    def test_format_docs_none_input(self):
        """Test formatting with None input"""
        result = _format_docs(None)
        assert result == ""


class TestWebSearch:
    """Test cases for the _web_search function"""
    
    @patch('rag.it_rag.tavily_search')
    def test_web_search_success(self, mock_tavily_search):
        """Test successful web search"""
        mock_tavily_search.return_value = "Web search results"
        
        input_dict = {"question": "How to configure VPN?"}
        result = _web_search(input_dict)
        
        assert result == "Web search results"
        mock_tavily_search.assert_called_once_with("How to configure VPN?")
    
    @patch('rag.it_rag.tavily_search')
    def test_web_search_different_questions(self, mock_tavily_search):
        """Test web search with different question types"""
        mock_tavily_search.return_value = "Search result"
        
        test_questions = [
            "Password reset procedure",
            "Network troubleshooting steps",
            "Software installation guide"
        ]
        
        for question in test_questions:
            input_dict = {"question": question}
            result = _web_search(input_dict)
            
            assert result == "Search result"
        
        # Verify tavily_search was called for each question
        assert mock_tavily_search.call_count == len(test_questions)


class TestLoadItRagChain:
    """Test cases for the load_it_rag_chain function"""
    
    @patch('rag.it_rag.BedrockEmbeddings')
    def test_load_it_rag_chain_missing_env_vars(self, mock_embeddings):
        """Test RAG chain loading with missing environment variables"""
        mock_embeddings.side_effect = KeyError("AWS_REGION")
        
        # Test with empty environment
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(KeyError):
                load_it_rag_chain()
    
    @patch('rag.it_rag.Chroma')
    @patch('rag.it_rag.BedrockEmbeddings')
    def test_load_it_rag_chain_chroma_exception(self, mock_embeddings, mock_chroma):
        """Test RAG chain loading with Chroma database exception"""
        mock_embeddings.return_value = Mock()
        mock_chroma.side_effect = Exception("Database connection failed")
        
        with patch.dict(os.environ, {
            "AWS_REGION": "us-east-1",
            "AWS_ACCESS_KEY_ID": "test_key_id",
            "AWS_SECRET_ACCESS_KEY": "test_secret_key"
        }):
            with pytest.raises(Exception) as exc_info:
                load_it_rag_chain()
            
            assert "Database connection failed" in str(exc_info.value)


class TestItRagIntegration:
    """Integration test cases for IT RAG functionality"""
    
    @patch('rag.it_rag.tavily_search')
    def test_format_docs_and_web_search_integration(self, mock_tavily_search):
        """Test integration between document formatting and web search"""
        # Test document formatting
        mock_doc1 = Mock()
        mock_doc1.page_content = "VPN setup instructions"
        mock_doc2 = Mock()
        mock_doc2.page_content = "Network configuration guide"
        
        formatted_docs = _format_docs([mock_doc1, mock_doc2])
        expected_docs = "VPN setup instructions\n\nNetwork configuration guide"
        assert formatted_docs == expected_docs
        
        # Test web search
        mock_tavily_search.return_value = "Additional web information"
        input_dict = {"question": "VPN troubleshooting"}
        web_result = _web_search(input_dict)
        
        assert web_result == "Additional web information"
        mock_tavily_search.assert_called_once_with("VPN troubleshooting")


if __name__ == "__main__":
    pytest.main([__file__])
