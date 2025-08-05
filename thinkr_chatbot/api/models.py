"""
Pydantic models for the ThinkR chatbot API.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="The user's message")
    use_context: bool = Field(True, description="Whether to use course material context")
    k_results: int = Field(5, description="Number of similar documents to retrieve")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="The chatbot's response")
    raw_response: str = Field(..., description="Raw response without formatting")
    references: List[Dict[str, Any]] = Field(default_factory=list, description="Course material references")
    context_used: bool = Field(..., description="Whether context was used")
    model: str = Field(..., description="Model used for response")
    timestamp: str = Field(..., description="Response timestamp")
    error: Optional[str] = Field(None, description="Error message if any")


class IndexResponse(BaseModel):
    """Response model for indexing operations."""
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Status message")
    stats: Optional[Dict[str, Any]] = Field(None, description="Indexing statistics")


class SystemInfoResponse(BaseModel):
    """Response model for system information."""
    model_name: str = Field(..., description="Current model name")
    temperature: float = Field(..., description="Model temperature")
    max_tokens: int = Field(..., description="Maximum tokens")
    vector_store_stats: Dict[str, Any] = Field(..., description="Vector store statistics")
    conversation_history_length: int = Field(..., description="Number of messages in history")
    pdf_directory: str = Field(..., description="PDF directory path")
    vector_db_path: str = Field(..., description="Vector database path")


class RecommendationRequest(BaseModel):
    """Request model for recommendations endpoint."""
    topic: str = Field(..., description="Topic for recommendations")
    num_recommendations: int = Field(3, description="Number of recommendations")


class RecommendationResponse(BaseModel):
    """Response model for recommendations endpoint."""
    topic: str = Field(..., description="Requested topic")
    recommendations: List[Dict[str, Any]] = Field(..., description="Learning recommendations")


class ConversationExportResponse(BaseModel):
    """Response model for conversation export."""
    conversation: Optional[List[Dict[str, Any]]] = Field(None, description="Conversation in JSON format")
    conversation_text: Optional[str] = Field(None, description="Conversation in text format")
    export_timestamp: str = Field(..., description="Export timestamp")
    total_messages: int = Field(..., description="Total number of messages") 