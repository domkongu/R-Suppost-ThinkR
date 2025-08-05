#!/usr/bin/env python3
"""
Demo script for the ThinkR chatbot.
This script demonstrates the basic functionality of the chatbot.
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from thinkr_chatbot.core.chatbot import ThinkRChatbot


def demo_chat():
    """Demo the chat functionality."""
    print("🤖 ThinkR Chatbot Demo")
    print("=" * 50)
    
    try:
        # Initialize chatbot
        print("Initializing chatbot...")
        chatbot = ThinkRChatbot()
        
        # Show system info
        info = chatbot.get_system_info()
        print(f"✅ Chatbot initialized successfully!")
        print(f"📊 Indexed documents: {info['vector_store_stats']['total_documents']}")
        print(f"🧠 Model: {info['model_name']}")
        print()
        
        # Demo questions
        demo_questions = [
            "How do I create a vector in R?",
            "What is the difference between <- and = in R?",
            "How do I install and load packages?",
            "What are data frames in R?",
            "How do I create plots in R?"
        ]
        
        print("💬 Demo Questions:")
        print("-" * 30)
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n{i}. {question}")
            print("🤔 Thinking...")
            
            try:
                result = chatbot.chat(question, use_context=True)
                
                if "error" in result:
                    print(f"❌ Error: {result['error']}")
                else:
                    print("✅ Response generated!")
                    print(f"📝 Response: {result['response'][:200]}...")
                    
                    if result.get('references'):
                        print(f"📚 References: {len(result['references'])} found")
                    
                    print(f"⏱️  Model: {result['model']}")
                    print(f"🔗 Context used: {result['context_used']}")
                
            except Exception as e:
                print(f"❌ Error processing question: {e}")
            
            print("-" * 30)
        
        # Demo recommendations
        print("\n🎯 Demo Recommendations:")
        print("-" * 30)
        
        topics = ["vectors", "data frames", "ggplot2"]
        
        for topic in topics:
            print(f"\n📖 Recommendations for '{topic}':")
            try:
                recommendations = chatbot.get_recommendations(topic, num_recommendations=2)
                
                if recommendations:
                    for rec in recommendations:
                        print(f"  • {rec['module']} (Page {rec['page']}) - {rec['suggestion']}")
                else:
                    print("  • No specific recommendations found")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        print("\n💡 Make sure you have:")
        print("  1. Set your OPENAI_API_KEY environment variable")
        print("  2. Installed all dependencies: pip install -e .")
        print("  3. Added PDF files to data/pdfs/ directory")
        print("  4. Run indexing: thinkr-chatbot index-pdfs")


def demo_setup():
    """Demo the setup process."""
    print("🔧 ThinkR Chatbot Setup Demo")
    print("=" * 50)
    
    # Check environment
    print("1. Checking environment...")
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("   ✅ OPENAI_API_KEY is set")
    else:
        print("   ❌ OPENAI_API_KEY not found")
        print("   💡 Set it with: export OPENAI_API_KEY='your_key_here'")
    
    # Check directories
    print("\n2. Checking directories...")
    pdf_dir = Path("data/pdfs")
    vector_dir = Path("data/vector_db")
    
    if pdf_dir.exists():
        pdf_files = list(pdf_dir.glob("*.pdf"))
        print(f"   ✅ PDF directory exists with {len(pdf_files)} PDF files")
    else:
        print("   ❌ PDF directory not found")
        print("   💡 Create it with: mkdir -p data/pdfs")
    
    if vector_dir.exists():
        print("   ✅ Vector database directory exists")
    else:
        print("   ❌ Vector database directory not found")
        print("   💡 Create it with: mkdir -p data/vector_db")
    
    # Check dependencies
    print("\n3. Checking dependencies...")
    try:
        import openai
        print("   ✅ OpenAI library available")
    except ImportError:
        print("   ❌ OpenAI library not found")
        print("   💡 Install with: pip install openai")
    
    try:
        import faiss
        print("   ✅ FAISS library available")
    except ImportError:
        print("   ❌ FAISS library not found")
        print("   💡 Install with: pip install faiss-cpu")
    
    try:
        import sentence_transformers
        print("   ✅ Sentence Transformers available")
    except ImportError:
        print("   ❌ Sentence Transformers not found")
        print("   💡 Install with: pip install sentence-transformers")
    
    print("\n✅ Setup check completed!")


def main():
    """Main demo function."""
    print("🚀 ThinkR Chatbot Demo")
    print("=" * 50)
    print()
    
    # Show setup info
    demo_setup()
    print()
    
    # Ask user if they want to continue
    response = input("Continue with chat demo? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        demo_chat()
    else:
        print("Demo ended. Run 'python demo.py' again to try the chat demo.")


if __name__ == "__main__":
    main() 