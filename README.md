## 🎉 ThinkR Chatbot

A full-featured chatbot system for ThinkR that helps students learn R programming. 

### 🎨 Project Structure
```
thinkr-chatbot/
├── thinkr_chatbot/
│   ├── core/
│   │   ├── chatbot.py          # Main chatbot logic
│   │   ├── vector_store.py     # FAISS integration
│   │   ├── pdf_processor.py    # PDF processing
│   │   └── prompt_manager.py   # System prompts
│   ├── api/
│   │   ├── main.py             # FastAPI endpoints
│   │   └── models.py           # Pydantic models
│   ├── web_app.py              # Streamlit interface
│   └── cli.py                  # Command line interface
├── data/
│   ├── pdfs/                   # Your R course PDFs
│   └── vector_db/              # FAISS index files
├── tests/
├── setup.py
├── requirements.txt
├── README.md
├── USAGE.md
└── demo.py
```

### 🛠️ Quick Start

1. **Install dependencies**:
   ```bash
   pip install -e .
   ```

2. **Set up environment**:
   ```bash
   cp config.env.example .env
   # Edit .env with your OpenAI API key
   ```

3. **Add your PDFs**:
   ```bash
   # Place your R course PDFs in data/pdfs/
   ```

4. **Index your materials**:
   ```bash
   thinkr-chatbot index-pdfs
   ```

5. **Start chatting**:
   ```bash
   # Web interface (recommended)
   streamlit run thinkr_chatbot/web_app.py
   
   # Command line
   thinkr-chatbot chat
   
   # API server
   uvicorn thinkr_chatbot.api.main:app --reload
   ```

### 🎯 System Prompt Integration

The system integrates your specified context:
- **System**: "You are a friendly R tutor at ThinkNeuro LLC. Refer to the course material if relevant, or just answer the question."
- **Context**: Automatically retrieved from your PDF materials
- **Answer**: General answer + references to relevant modules with timestamps

### 📊 Response Format

The chatbot provides:
1. **General Answer**: Comprehensive educational response
2. **Module References**: Direct links to relevant course modules
3. **Timestamps**: When available from your materials
4. **Code Examples**: Practical R code snippets

### 🔧 Advanced Features

- **Multiple PDF processors** (PyMuPDF, pdfplumber, pypdf)
- **Smart text chunking** with R code block preservation
- **Timestamp extraction** from course materials
- **Conversation history** management
- **Export functionality** (JSON/text)
- **Learning recommendations** based on topics
- **Batch processing** capabilities

### 🎨 Beautiful Interfaces

1. **Web Interface**: Modern Streamlit app with:
   - Real-time chat
   - Settings panel
   - Quick action buttons
   - System statistics
   - Export functionality

2. **CLI Interface**: Rich terminal interface with:
   - Interactive chat
   - Single question mode
   - Recommendations
   - System info

3. **API Interface**: RESTful API with:
   - Chat endpoints
   - Indexing endpoints
   - System info
   - Recommendations

### 📖 Documentation

- **README.md**: Comprehensive project overview
- **USAGE.md**: Detailed usage guide
- **demo.py**: Interactive demo script
- **tests/**: Unit tests for all components

The system is production-ready and follows best practices for:
- Error handling
- Logging
- Configuration management
- Testing
- Documentation

You can now add your R course PDF files to `data/pdfs/`, run the indexing, and start helping students learn R programming with your personalized ThinkR chatbot! 🎓 # R-Suppost-ThinkR
