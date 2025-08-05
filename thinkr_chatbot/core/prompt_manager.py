"""
Prompt management for the ThinkR chatbot.
"""

from typing import List, Dict, Any
import os
from dataclasses import dataclass


@dataclass
class ChatMessage:
    """Represents a chat message with role and content."""
    role: str
    content: str
    timestamp: str = None


class PromptManager:
    """Manages system prompts and message formatting for the ThinkR chatbot."""
    
    def __init__(self):
        self.system_prompt = self._get_system_prompt()
        self.conversation_history: List[ChatMessage] = []
    
    def _get_system_prompt(self) -> str:
        """Get the main system prompt for the R tutor."""
        return """You are a friendly R tutor at ThinkNeuro LLC. Your role is to help students learn R programming effectively.

Key responsibilities:
1. **Answer R Programming Questions**: Provide clear, accurate explanations of R concepts, syntax, and best practices
2. **Reference Course Material**: When relevant, refer to specific modules, sections, or timestamps from the course material
3. **Provide Code Examples**: Give practical, runnable R code examples when appropriate
4. **Encourage Learning**: Foster a supportive learning environment
5. **Correct Misconceptions**: Gently correct misunderstandings about R programming

Response format:
- **General Answer**: Provide a comprehensive, educational response
- **Module Reference**: If applicable, reference specific course modules with timestamps
- **Code Examples**: Include relevant R code snippets when helpful
- **Next Steps**: Suggest related topics or practice exercises when appropriate

Remember:
- Be encouraging and patient with learners
- Use clear, accessible language
- Provide context for R concepts
- Encourage hands-on practice
- Reference specific course materials when relevant

Context from course materials will be provided to help you give more accurate and relevant responses."""

    def get_messages_with_context(self, user_message: str, context: str = None) -> List[Dict[str, str]]:
        """Format messages for the LLM with context."""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add context if provided
        if context:
            context_message = f"Relevant course material context:\n{context}\n\nUser question: {user_message}"
            messages.append({"role": "user", "content": context_message})
        else:
            messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def add_to_history(self, role: str, content: str, timestamp: str = None):
        """Add a message to conversation history."""
        message = ChatMessage(role=role, content=content, timestamp=timestamp)
        self.conversation_history.append(message)
    
    def get_recent_history(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation history for context."""
        recent_messages = self.conversation_history[-max_messages:] if self.conversation_history else []
        return [{"role": msg.role, "content": msg.content} for msg in recent_messages]
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
    
    def format_response_with_references(self, response: str, references: List[Dict[str, Any]] = None) -> str:
        """Format the response with module references and timestamps."""
        formatted_response = response
        
        if references:
            formatted_response += "\n\n**Relevant Course References:**\n"
            for ref in references:
                module = ref.get('module', 'Unknown Module')
                timestamp = ref.get('timestamp', 'N/A')
                page = ref.get('page', '')
                
                ref_text = f"- **{module}**"
                if timestamp != 'N/A':
                    ref_text += f" (Timestamp: {timestamp})"
                if page:
                    ref_text += f" (Page: {page})"
                
                formatted_response += ref_text + "\n"
        
        return formatted_response 