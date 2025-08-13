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

### 🔧 Advanced Features

- **Multiple PDF processors** (PyMuPDF, pdfplumber, pypdf)
- **Smart text chunking** with R code block preservation
- **Timestamp extraction** from course materials
- **Export functionality** (JSON/text)
- **Learning recommendations** based on topics
- **Batch processing** capabilities

