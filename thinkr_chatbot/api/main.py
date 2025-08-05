"""
FastAPI application for the ThinkR chatbot.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import List

from .models import (
    ChatRequest, ChatResponse, IndexResponse, SystemInfoResponse,
    RecommendationRequest, RecommendationResponse, ConversationExportResponse
)
from ..core.chatbot import ThinkRChatbot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ThinkR Chatbot API",
    description="A friendly R tutor chatbot for students learning R programming",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot (will be created on first request)
chatbot: ThinkRChatbot = None


def get_chatbot() -> ThinkRChatbot:
    """Get or create the chatbot instance."""
    global chatbot
    if chatbot is None:
        try:
            chatbot = ThinkRChatbot()
            logger.info("Chatbot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize chatbot: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize chatbot")
    return chatbot


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to ThinkR Chatbot API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        bot = get_chatbot()
        return {"status": "healthy", "chatbot_initialized": True}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint for interacting with the R tutor."""
    try:
        bot = get_chatbot()
        result = bot.chat(
            message=request.message,
            use_context=request.use_context,
            k_results=request.k_results
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index-pdfs", response_model=IndexResponse)
async def index_pdfs(background_tasks: BackgroundTasks):
    """Index PDF documents in the background."""
    try:
        bot = get_chatbot()
        
        # Run indexing in background
        def index_task():
            try:
                result = bot.index_pdfs()
                logger.info(f"Background indexing completed: {result}")
            except Exception as e:
                logger.error(f"Background indexing failed: {e}")
        
        background_tasks.add_task(index_task)
        
        return IndexResponse(
            status="started",
            message="PDF indexing started in background"
        )
        
    except Exception as e:
        logger.error(f"Error starting PDF indexing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update-index", response_model=IndexResponse)
async def update_index(background_tasks: BackgroundTasks):
    """Update the vector index with new PDF documents."""
    try:
        bot = get_chatbot()
        
        # Run update in background
        def update_task():
            try:
                result = bot.update_index()
                logger.info(f"Background index update completed: {result}")
            except Exception as e:
                logger.error(f"Background index update failed: {e}")
        
        background_tasks.add_task(update_task)
        
        return IndexResponse(
            status="started",
            message="Index update started in background"
        )
        
    except Exception as e:
        logger.error(f"Error starting index update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/system-info", response_model=SystemInfoResponse)
async def get_system_info():
    """Get system information and statistics."""
    try:
        bot = get_chatbot()
        info = bot.get_system_info()
        return SystemInfoResponse(**info)
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Get learning recommendations based on a topic."""
    try:
        bot = get_chatbot()
        recommendations = bot.get_recommendations(
            topic=request.topic,
            num_recommendations=request.num_recommendations
        )
        
        return RecommendationResponse(
            topic=request.topic,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/batch")
async def batch_chat(messages: List[str]):
    """Process multiple chat messages in batch."""
    try:
        bot = get_chatbot()
        results = bot.batch_chat(messages)
        return {"results": results}
        
    except Exception as e:
        logger.error(f"Error in batch chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/conversation/clear")
async def clear_conversation():
    """Clear the conversation history."""
    try:
        bot = get_chatbot()
        bot.clear_conversation_history()
        return {"message": "Conversation history cleared"}
        
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversation/export", response_model=ConversationExportResponse)
async def export_conversation(format: str = "json"):
    """Export conversation history."""
    try:
        bot = get_chatbot()
        export_data = bot.export_conversation(format=format)
        return ConversationExportResponse(**export_data)
        
    except Exception as e:
        logger.error(f"Error exporting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
async def search_documents(query: str, k: int = 5):
    """Search for similar documents."""
    try:
        bot = get_chatbot()
        results = bot.get_similar_documents(query, k=k)
        return {"query": query, "results": results}
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 