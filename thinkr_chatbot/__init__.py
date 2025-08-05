"""
ThinkR Chatbot - A friendly R tutor for students learning R programming.
"""

__version__ = "0.1.0"
__author__ = "ThinkNeuro LLC"
__email__ = "info@thinkneuro.com"

from .core.chatbot import ThinkRChatbot
from .core.vector_store import VectorStore
from .core.pdf_processor import PDFProcessor

__all__ = ["ThinkRChatbot", "VectorStore", "PDFProcessor"] 