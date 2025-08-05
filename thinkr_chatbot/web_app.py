"""
Streamlit web interface for the ThinkR chatbot.
"""

import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path
import pandas as pd

from .core.chatbot import ThinkRChatbot

# Page configuration
st.set_page_config(
    page_title="ThinkR Chatbot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .reference-box {
        background-color: #fff3e0;
        border: 1px solid #ff9800;
        border-radius: 0.5rem;
        padding: 0.5rem;
        margin: 0.5rem 0;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_chatbot():
    """Initialize the chatbot."""
    try:
        return ThinkRChatbot()
    except Exception as e:
        st.error(f"Failed to initialize chatbot: {str(e)}")
        st.info("Please make sure you have set your OPENAI_API_KEY environment variable.")
        return None


def display_chat_message(role, content, references=None):
    """Display a chat message with proper styling."""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>ThinkR Tutor:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
        
        # Display references if available
        if references:
            st.markdown("**Course References:**")
            for i, ref in enumerate(references, 1):
                module = ref.get('module', 'Unknown Module')
                page = ref.get('page', 'N/A')
                score = ref.get('score', 0)
                
                st.markdown(f"""
                <div class="reference-box">
                    <strong>Reference {i}:</strong> {module}<br>
                    <small>Page: {page} | Relevance: {score:.3f}</small>
                </div>
                """, unsafe_allow_html=True)


def main():
    """Main application."""
    # Header
    st.markdown('<h1 class="main-header">🤖 ThinkR Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Your friendly R programming tutor</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<h2 class="sidebar-header">⚙️ Settings</h2>', unsafe_allow_html=True)
        
        # Model settings
        model_name = st.selectbox(
            "Model",
            ["gpt-4", "gpt-3.5-turbo"],
            index=0
        )
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Controls randomness in responses"
        )
        
        max_tokens = st.slider(
            "Max Tokens",
            min_value=100,
            max_value=2000,
            value=1000,
            step=100,
            help="Maximum length of response"
        )
        
        use_context = st.checkbox(
            "Use Course Context",
            value=True,
            help="Include relevant course material in responses"
        )
        
        k_results = st.slider(
            "Context Results",
            min_value=1,
            max_value=10,
            value=5,
            help="Number of similar documents to retrieve"
        )
        
        # System info
        st.markdown('<h3 class="sidebar-header">📊 System Info</h3>', unsafe_allow_html=True)
        
        if 'chatbot' not in st.session_state:
            st.session_state.chatbot = initialize_chatbot()
        
        if st.session_state.chatbot:
            info = st.session_state.chatbot.get_system_info()
            
            st.metric("Indexed Documents", info["vector_store_stats"]["total_documents"])
            st.metric("Conversation History", info["conversation_history_length"])
            st.metric("Model", info["model_name"])
            
            # Actions
            st.markdown('<h3 class="sidebar-header">🔧 Actions</h3>', unsafe_allow_html=True)
            
            if st.button("🔄 Refresh Index"):
                with st.spinner("Refreshing index..."):
                    result = st.session_state.chatbot.update_index()
                    if result["status"] == "success":
                        st.success("Index refreshed successfully!")
                    else:
                        st.warning(result["message"])
            
            if st.button("🗑️ Clear History"):
                st.session_state.chatbot.clear_conversation_history()
                st.session_state.messages = []
                st.success("Conversation history cleared!")
            
            if st.button("📊 Export Chat"):
                export_data = st.session_state.chatbot.export_conversation("json")
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"thinkr_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    # Main chat area
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        for message in st.session_state.messages:
            display_chat_message(
                message["role"],
                message["content"],
                message.get("references")
            )
        
        # Chat input
        user_input = st.text_area(
            "Ask me about R programming:",
            height=100,
            placeholder="Type your question here..."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Send", type="primary"):
                if user_input.strip() and st.session_state.chatbot:
                    # Add user message to chat
                    st.session_state.messages.append({
                        "role": "user",
                        "content": user_input,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Get response
                    with st.spinner("Thinking..."):
                        result = st.session_state.chatbot.chat(
                            user_input,
                            use_context=use_context,
                            k_results=k_results
                        )
                    
                    # Add assistant response to chat
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["response"],
                        "references": result.get("references", []),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Rerun to display new messages
                    st.rerun()
        
        with col2:
            if st.button("💡 Get Recommendations"):
                if user_input.strip() and st.session_state.chatbot:
                    with st.spinner("Finding recommendations..."):
                        recommendations = st.session_state.chatbot.get_recommendations(user_input)
                    
                    if recommendations:
                        st.markdown("**Learning Recommendations:**")
                        for rec in recommendations:
                            st.markdown(f"• **{rec['module']}** (Page {rec['page']}) - {rec['suggestion']}")
                    else:
                        st.info("No specific recommendations found for this topic.")
    
    # Right column for additional features
    with col3:
        st.markdown('<h3 class="sidebar-header">📚 Quick Actions</h3>', unsafe_allow_html=True)
        
        # Quick questions
        st.markdown("**Common Questions:**")
        
        quick_questions = [
            "How do I create a vector in R?",
            "What is the difference between <- and = in R?",
            "How do I install and load packages?",
            "What are data frames in R?",
            "How do I create plots in R?"
        ]
        
        for question in quick_questions:
            if st.button(question, key=f"quick_{question}"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": question,
                    "timestamp": datetime.now().isoformat()
                })
                
                with st.spinner("Thinking..."):
                    result = st.session_state.chatbot.chat(
                        question,
                        use_context=use_context,
                        k_results=k_results
                    )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["response"],
                    "references": result.get("references", []),
                    "timestamp": datetime.now().isoformat()
                })
                
                st.rerun()
        
        # System statistics
        if st.session_state.chatbot:
            st.markdown('<h3 class="sidebar-header">📈 Statistics</h3>', unsafe_allow_html=True)
            
            info = st.session_state.chatbot.get_system_info()
            stats_data = {
                "Metric": [
                    "Total Documents",
                    "Index Size",
                    "Vector Dimension",
                    "Conversation Length"
                ],
                "Value": [
                    info["vector_store_stats"]["total_documents"],
                    info["vector_store_stats"]["index_size"],
                    info["vector_store_stats"]["dimension"],
                    info["conversation_history_length"]
                ]
            }
            
            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, hide_index=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666;">Built with ❤️ by ThinkNeuro LLC</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main() 