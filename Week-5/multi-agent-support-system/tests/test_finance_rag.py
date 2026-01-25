import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rag.finance_rag import _format_docs, _web_search, load_finance_rag_chain


class TestFormatDocs:
    """Test cases for the _format_docs utility function"""
    
    def test_format_docs_with_documents(self):
        """Test formatting multiple documents"""
        mock_doc1 = Mock()
        mock_doc1.page_content = "Payroll policy details"
        mock_doc2 = Mock()
        mock_doc2.page_content = "Expense reimbursement process"
        mock_doc3 = Mock()
        mock_doc3.page_content = "Budget approval workflow"
        
        docs = [mock_doc1, mock_doc2, mock_doc3]
        result = _format_docs(docs)
        
        expected = "Payroll policy details\n\nExpense reimbursement process\n\nBudget approval workflow"
        assert result == expected
    
    def test_format_docs_single_document(self):
        """Test formatting single document"""
        mock_doc = Mock()
        mock_doc.page_content = "Financial policy document"
        
        result = _format_docs([mock_doc])
        assert result == "Financial policy document"
    
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
    
    @patch('rag.finance_rag.tavily_search')
    def test_web_search_success(self, mock_tavily_search):
        """Test successful web search"""
        mock_tavily_search.return_value = "Finance web search results"
        
        input_dict = {"question": "What are current tax rates?"}
        result = _web_search(input_dict)
        
        assert result == "Finance web search results"
        mock_tavily_search.assert_called_once_with("What are current tax rates?")
    
    @patch('rag.finance_rag.tavily_search')
    def test_web_search_different_questions(self, mock_tavily_search):
        """Test web search with different question types"""
        mock_tavily_search.return_value = "Search result"
        
        test_questions = [
            "Payroll processing guidelines",
            "Invoice approval workflow",
            "Expense reporting requirements"
        ]
        
        for question in test_questions:
            input_dict = {"question": question}
            result = _web_search(input_dict)
            
            assert result == "Search result"
        
        # Verify tavily_search was called for each question
        assert mock_tavily_search.call_count == len(test_questions)


class TestLoadFinanceRagChain:
    """Test cases for the load_finance_rag_chain function"""
    
    @patch('rag.finance_rag.BedrockEmbeddings')
    def test_load_finance_rag_chain_missing_env_vars(self, mock_embeddings):
        """Test finance RAG chain loading with missing environment variables"""
        mock_embeddings.side_effect = KeyError("AWS_REGION")
        
        # Test with empty environment
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(KeyError):
                load_finance_rag_chain()
    
    @patch('rag.finance_rag.Chroma')
    @patch('rag.finance_rag.BedrockEmbeddings')
    def test_load_finance_rag_chain_chroma_exception(self, mock_embeddings, mock_chroma):
        """Test finance RAG chain loading with Chroma database exception"""
        mock_embeddings.return_value = Mock()
        mock_chroma.side_effect = Exception("Finance database connection failed")
        
        with patch.dict(os.environ, {
            "AWS_REGION": "us-east-1",
            "AWS_ACCESS_KEY_ID": "test_key_id",
            "AWS_SECRET_ACCESS_KEY": "test_secret_key"
        }):
            with pytest.raises(Exception) as exc_info:
                load_finance_rag_chain()
            
            assert "Finance database connection failed" in str(exc_info.value)


class TestFinanceRagIntegration:
    """Integration test cases for Finance RAG functionality"""
    
    @patch('rag.finance_rag.tavily_search')
    def test_format_docs_and_web_search_integration(self, mock_tavily_search):
        """Test integration between document formatting and web search"""
        # Test document formatting
        mock_doc1 = Mock()
        mock_doc1.page_content = "Payroll processing guidelines"
        mock_doc2 = Mock()
        mock_doc2.page_content = "Expense reimbursement policy"
        
        formatted_docs = _format_docs([mock_doc1, mock_doc2])
        expected_docs = "Payroll processing guidelines\n\nExpense reimbursement policy"
        assert formatted_docs == expected_docs
        
        # Test web search
        mock_tavily_search.return_value = "Additional finance information"
        input_dict = {"question": "Tax rate updates"}
        web_result = _web_search(input_dict)
        
        assert web_result == "Additional finance information"
        mock_tavily_search.assert_called_once_with("Tax rate updates")


if __name__ == "__main__":
    pytest.main([__file__])
