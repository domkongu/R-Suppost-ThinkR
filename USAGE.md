# ThinkR Chatbot Usage Guide

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd thinkr-chatbot

# Install dependencies
pip install -e .

# Set up environment
cp config.env.example .env
# Edit .env with your OpenAI API key
```

### 2. Add Your Course Materials

Place your R course PDF files in the `data/pdfs/` directory:

```bash
mkdir -p data/pdfs
# Copy your PDF files to data/pdfs/
```

### 3. Index Your Materials

```bash
# Index PDFs for the first time
thinkr-chatbot index-pdfs

# Or force re-indexing
thinkr-chatbot index-pdfs --force
```

### 4. Start Chatting

#### Web Interface (Recommended)
```bash
streamlit run thinkr_chatbot/web_app.py
```

#### Command Line Interface
```bash
# Interactive chat
thinkr-chatbot chat

# Single question
thinkr-chatbot ask "How do I create a vector in R?"

# Get recommendations
thinkr-chatbot recommend "data frames"
```

#### API Server
```bash
uvicorn thinkr_chatbot.api.main:app --reload
```

## Features

### 🤖 Intelligent R Tutoring
- Context-aware responses based on your course materials
- Code examples and explanations
- Best practices and common pitfalls

### 📚 PDF Integration
- Process and index your own R course PDFs
- Automatic text extraction and chunking
- Metadata preservation (page numbers, titles, etc.)

### 🔍 FAISS Vector Database
- Fast similarity search
- Efficient document retrieval
- Scalable indexing

### 💬 Multiple Interfaces
- **Web UI**: Beautiful Streamlit interface
- **CLI**: Command-line interface for power users
- **API**: RESTful API for integration

### 🎯 Module References
- Direct links to relevant course modules
- Page numbers and timestamps
- Relevance scores

## Configuration

### Environment Variables

Create a `.env` file with your configuration:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
MODEL_NAME=gpt-4
TEMPERATURE=0.7
MAX_TOKENS=1000
VECTOR_DB_PATH=./data/vector_db
PDF_DIR=./data/pdfs
```

### Model Settings

- **Model**: Choose between `gpt-4` (recommended) or `gpt-3.5-turbo`
- **Temperature**: Controls randomness (0.0 = deterministic, 1.0 = very random)
- **Max Tokens**: Maximum response length

## Usage Examples

### Web Interface

1. **Start the web app**:
   ```bash
   streamlit run thinkr_chatbot/web_app.py
   ```

2. **Configure settings** in the sidebar:
   - Choose your model
   - Adjust temperature and max tokens
   - Enable/disable course context

3. **Ask questions** in the chat interface:
   - Type your R programming questions
   - Use quick action buttons for common questions
   - Get learning recommendations

### Command Line

#### Interactive Chat
```bash
thinkr-chatbot chat
```

Available commands:
- `clear` - Clear conversation history
- `stats` - Show system statistics
- `help` - Show help
- `quit` or `exit` - End session

#### Single Questions
```bash
# Basic question
thinkr-chatbot ask "How do I install packages in R?"

# Save response to file
thinkr-chatbot ask "What are data frames?" --output response.txt

# Get JSON response
thinkr-chatbot ask "Explain vectors" --format json --output response.json
```

#### Recommendations
```bash
# Get learning recommendations
thinkr-chatbot recommend "ggplot2"

# Get more recommendations
thinkr-chatbot recommend "statistics" --count 5
```

#### System Information
```bash
# Show system stats
thinkr-chatbot info

# Export conversation
thinkr-chatbot export --format json --output chat.json
```

### API Usage

#### Start the API Server
```bash
uvicorn thinkr_chatbot.api.main:app --reload
```

#### API Endpoints

**Chat**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I create a vector in R?",
    "use_context": true,
    "k_results": 5
  }'
```

**Index PDFs**
```bash
curl -X POST "http://localhost:8000/index-pdfs"
```

**Get System Info**
```bash
curl "http://localhost:8000/system-info"
```

**Get Recommendations**
```bash
curl -X POST "http://localhost:8000/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "data frames",
    "num_recommendations": 3
  }'
```

## Advanced Features

### Custom PDF Processing

The system automatically handles:
- Text extraction from PDFs
- Code block preservation
- Timestamp extraction
- Metadata preservation

### Vector Search

- **Similarity Search**: Find relevant course materials
- **Context Integration**: Include relevant content in responses
- **Reference Tracking**: Link responses to specific modules/pages

### Conversation Management

- **History**: Maintain conversation context
- **Export**: Save conversations in JSON or text format
- **Clear**: Reset conversation history

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   ```
   Error: OpenAI API key is required
   ```
   **Solution**: Set your `OPENAI_API_KEY` environment variable

2. **No PDFs Found**
   ```
   Warning: No PDF chunks found to index
   ```
   **Solution**: Add PDF files to `data/pdfs/` directory

3. **FAISS Import Error**
   ```
   Error: FAISS or sentence-transformers not available
   ```
   **Solution**: Install dependencies: `pip install faiss-cpu sentence-transformers`

4. **Memory Issues**
   ```
   Error: Out of memory
   ```
   **Solution**: Reduce chunk size or use smaller embedding model

### Performance Tips

1. **Indexing**: Run indexing in background for large PDF collections
2. **Chunk Size**: Adjust chunk size based on your content (default: 1000 chars)
3. **Model Selection**: Use `gpt-3.5-turbo` for faster responses, `gpt-4` for better quality
4. **Context Results**: Reduce `k_results` for faster responses

### Development

#### Running Tests
```bash
pytest tests/
```

#### Code Formatting
```bash
black thinkr_chatbot/
flake8 thinkr_chatbot/
```

#### Adding New Features
1. Extend the core classes in `thinkr_chatbot/core/`
2. Add API endpoints in `thinkr_chatbot/api/`
3. Update the CLI in `thinkr_chatbot/cli.py`
4. Enhance the web interface in `thinkr_chatbot/web_app.py`

## Support

- **Documentation**: Check the README.md for detailed information
- **Issues**: Report bugs on GitHub
- **Email**: Contact info@thinkneuro.com for support

## License

MIT License - see LICENSE file for details. 