"""
Tests for the ThinkR chatbot.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from pathlib import Path

from thinkr_chatbot.core.chatbot import ThinkRChatbot
from thinkr_chatbot.core.vector_store import VectorStore
from thinkr_chatbot.core.pdf_processor import PDFProcessor
from thinkr_chatbot.core.prompt_manager import PromptManager


class TestPromptManager:    
    def test_init(self):
        """Test prompt manager initialization."""
        pm = PromptManager()
        assert pm.system_prompt is not None
        assert len(pm.conversation_history) == 0
    
    def test_get_messages_with_context(self):
        """Test message formatting with context."""
        pm = PromptManager()
        messages = pm.get_messages_with_context("test message", "test context")
        
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert "test context" in messages[1]["content"]
        assert "test message" in messages[1]["content"]
    
    def test_add_to_history(self):
        """Test adding messages to history."""
        pm = PromptManager()
        pm.add_to_history("user", "test message")
        
        assert len(pm.conversation_history) == 1
        assert pm.conversation_history[0].role == "user"
        assert pm.conversation_history[0].content == "test message"
    
    def test_clear_history(self):
        """Test clearing conversation history."""
        pm = PromptManager()
        pm.add_to_history("user", "test message")
        pm.clear_history()
        
        assert len(pm.conversation_history) == 0


class TestPDFProcessor:
    """Test the PDF processor."""
    
    def test_init(self):
        """Test PDF processor initialization."""
        processor = PDFProcessor()
        assert processor.chunk_size == 1000
        assert processor.chunk_overlap == 200
    
    def test_split_into_sentences(self):
        """Test sentence splitting with R code blocks."""
        processor = PDFProcessor()
        text = "This is a sentence. ```r\nx <- 1\n``` This is another sentence."
        sentences = processor._split_into_sentences(text)
        
        assert len(sentences) == 2
        assert "```r\nx <- 1\n```" in sentences[0]
    
    def test_extract_timestamps(self):
        """Test timestamp extraction."""
        processor = PDFProcessor()
        text = "At 12:34 we discussed vectors. Later at 1:23:45 we covered data frames."
        timestamps = processor.extract_timestamps(text)
        
        assert "12:34" in timestamps
        assert "1:23:45" in timestamps


class TestVectorStore:
    """Test the vector store."""
    
    @patch('thinkr_chatbot.core.vector_store.SentenceTransformer')
    @patch('thinkr_chatbot.core.vector_store.faiss')
    def test_init(self, mock_faiss, mock_transformer):
        """Test vector store initialization."""
        mock_transformer.return_value.get_sentence_embedding_dimension.return_value = 384
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(index_path=temp_dir)
            assert vector_store.dimension == 384
            assert len(vector_store.metadata) == 0
    
    @patch('thinkr_chatbot.core.vector_store.SentenceTransformer')
    @patch('thinkr_chatbot.core.vector_store.faiss')
    def test_add_documents(self, mock_faiss, mock_transformer):
        """Test adding documents to vector store."""
        mock_transformer.return_value.get_sentence_embedding_dimension.return_value = 384
        mock_transformer.return_value.encode.return_value = [[0.1] * 384]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(index_path=temp_dir)
            
            documents = [
                {"text": "test document 1", "metadata": {"source": "test1"}},
                {"text": "test document 2", "metadata": {"source": "test2"}}
            ]
            
            vector_store.add_documents(documents)
            assert len(vector_store.metadata) == 2


class TestThinkRChatbot:
    """Test the main chatbot."""
    
    @patch('thinkr_chatbot.core.chatbot.openai')
    @patch('thinkr_chatbot.core.vector_store.SentenceTransformer')
    @patch('thinkr_chatbot.core.vector_store.faiss')
    def test_init(self, mock_faiss, mock_transformer, mock_openai):
        """Test chatbot initialization."""
        mock_transformer.return_value.get_sentence_embedding_dimension.return_value = 384
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chatbot = ThinkRChatbot(
                openai_api_key="test_key",
                vector_db_path=temp_dir,
                pdf_dir=temp_dir
            )
            
            assert chatbot.model_name == "gpt-4"
            assert chatbot.temperature == 0.7
            assert chatbot.max_tokens == 1000
    
    @patch('thinkr_chatbot.core.chatbot.openai')
    @patch('thinkr_chatbot.core.vector_store.SentenceTransformer')
    @patch('thinkr_chatbot.core.vector_store.faiss')
    def test_chat_without_context(self, mock_faiss, mock_transformer, mock_openai):
        """Test chat without context."""
        mock_transformer.return_value.get_sentence_embedding_dimension.return_value = 384
        mock_openai.ChatCompletion.create.return_value.choices[0].message.content = "Test response"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chatbot = ThinkRChatbot(
                openai_api_key="test_key",
                vector_db_path=temp_dir,
                pdf_dir=temp_dir
            )
            
            result = chatbot.chat("test message", use_context=False)
            
            assert "response" in result
            assert result["model"] == "gpt-4"
            assert not result["context_used"]
    
    def test_get_system_info(self):
        """Test getting system information."""
        with tempfile.TemporaryDirectory() as temp_dir:
            chatbot = ThinkRChatbot(
                openai_api_key="test_key",
                vector_db_path=temp_dir,
                pdf_dir=temp_dir
            )
            
            info = chatbot.get_system_info()
            
            assert "model_name" in info
            assert "temperature" in info
            assert "max_tokens" in info
            assert "vector_store_stats" in info


if __name__ == "__main__":
    pytest.main([__file__]) 
