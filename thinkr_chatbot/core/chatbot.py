"""
Main chatbot class for ThinkR - A friendly R tutor for students.
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime
import openai
from dotenv import load_dotenv

from .vector_store import VectorStore
from .pdf_processor import PDFProcessor
from .prompt_manager import PromptManager

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class ThinkRChatbot:
    """Simple chatbot for ThinkR R tutoring."""
    
    def __init__(self, 
                 openai_api_key: str = None,
                 model_name: str = "gpt-4",
                 temperature: float = 0.7,
                 max_tokens: int = 1000):
        
        # Initialize OpenAI
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        openai.api_key = self.api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize components
        self.vector_store = VectorStore()
        self.pdf_processor = PDFProcessor()
        self.prompt_manager = PromptManager()
        
        logger.info(f"ThinkR Chatbot initialized with model: {model_name}")
    
    def index_pdfs(self, pdf_dir: str = "./data/pdfs") -> Dict[str, Any]:
        """Index PDF documents for retrieval."""
        logger.info(f"Indexing PDFs from: {pdf_dir}")
        
        # Process PDFs
        chunks = self.pdf_processor.process_pdf_directory(pdf_dir)
        
        if not chunks:
            return {"status": "warning", "message": "No PDF chunks found to index"}
        
        # Add to vector store
        self.vector_store.add_documents(chunks)
        
        stats = self.vector_store.get_index_stats()
        logger.info(f"Indexed {stats['total_documents']} documents")
        
        return {
            "status": "success",
            "message": f"Successfully indexed {stats['total_documents']} documents",
            "stats": stats
        }
    
    def chat(self, message: str, use_context: bool = True) -> Dict[str, Any]:
        """Process a chat message and return a response."""
        try:
            # Get relevant context from vector store
            context = ""
            references = []
            
            if use_context:
                context, references = self.vector_store.search_with_context(message, k=5)
            
            # Format messages for OpenAI
            messages = self.prompt_manager.get_messages_with_context(message, context)
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract response
            assistant_message = response.choices[0].message.content
            
            # Format response with references
            formatted_response = self.prompt_manager.format_response_with_references(
                assistant_message, references
            )
            
            # Add to conversation history
            self.prompt_manager.add_to_history("user", message)
            self.prompt_manager.add_to_history("assistant", assistant_message)
            
            # Prepare response
            result = {
                "response": formatted_response,
                "raw_response": assistant_message,
                "references": references,
                "context_used": bool(context),
                "model": self.model_name,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Generated response with {len(references)} references")
            return result
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {
                "response": "I apologize, but I encountered an error while processing your request. Please try again.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_recommendations(self, topic: str, num_recommendations: int = 3) -> List[Dict[str, Any]]:
        """Get learning recommendations based on a topic."""
        similar_docs = self.vector_store.similarity_search(topic, k=num_recommendations)
        
        recommendations = []
        for doc in similar_docs:
            metadata = doc['metadata']
            recommendation = {
                'topic': topic,
                'module': metadata.get('title', 'Unknown Module'),
                'page': metadata.get('page', ''),
                'source': metadata.get('source', ''),
                'relevance_score': doc['score'],
                'suggestion': f"Review {metadata.get('title', 'this module')} on page {metadata.get('page', 'N/A')}"
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.prompt_manager.clear_history()
        logger.info("Conversation history cleared")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information and statistics."""
        vector_stats = self.vector_store.get_index_stats()
        
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "vector_store_stats": vector_stats,
            "conversation_history_length": len(self.prompt_manager.conversation_history)
        } 