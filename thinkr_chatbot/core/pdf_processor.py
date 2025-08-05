"""
PDF processing utilities for extracting and chunking text from R course materials.
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from datetime import datetime

try:
    import pypdf
    import pdfplumber
    import fitz  # PyMuPDF
except ImportError as e:
    logging.warning(f"PDF processing libraries not available: {e}")

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Process PDF files to extract text and metadata for indexing."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text and metadata from a PDF file."""
        try:
            # Try PyMuPDF first (better for complex layouts)
            return self._extract_with_pymupdf(pdf_path)
        except Exception as e:
            logger.warning(f"PyMuPDF failed, trying pdfplumber: {e}")
            try:
                return self._extract_with_pdfplumber(pdf_path)
            except Exception as e2:
                logger.warning(f"pdfplumber failed, trying pypdf: {e2}")
                return self._extract_with_pypdf(pdf_path)
    
    def _extract_with_pymupdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text using PyMuPDF."""
        doc = fitz.open(pdf_path)
        text_content = []
        metadata = {
            'title': doc.metadata.get('title', ''),
            'author': doc.metadata.get('author', ''),
            'subject': doc.metadata.get('subject', ''),
            'creator': doc.metadata.get('creator', ''),
            'producer': doc.metadata.get('producer', ''),
            'creation_date': doc.metadata.get('creationDate', ''),
            'modification_date': doc.metadata.get('modDate', ''),
            'total_pages': len(doc)
        }
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                text_content.append({
                    'page': page_num + 1,
                    'text': text.strip(),
                    'bbox': page.rect
                })
        
        doc.close()
        
        return {
            'text_content': text_content,
            'metadata': metadata,
            'filename': os.path.basename(pdf_path)
        }
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text using pdfplumber."""
        with pdfplumber.open(pdf_path) as pdf:
            text_content = []
            metadata = {
                'title': pdf.metadata.get('Title', ''),
                'author': pdf.metadata.get('Author', ''),
                'subject': pdf.metadata.get('Subject', ''),
                'creator': pdf.metadata.get('Creator', ''),
                'producer': pdf.metadata.get('Producer', ''),
                'total_pages': len(pdf.pages)
            }
            
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and text.strip():
                    text_content.append({
                        'page': page_num + 1,
                        'text': text.strip(),
                        'bbox': page.bbox if hasattr(page, 'bbox') else None
                    })
            
            return {
                'text_content': text_content,
                'metadata': metadata,
                'filename': os.path.basename(pdf_path)
            }
    
    def _extract_with_pypdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text using pypdf (fallback)."""
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            text_content = []
            metadata = {
                'title': reader.metadata.get('/Title', '') if reader.metadata else '',
                'author': reader.metadata.get('/Author', '') if reader.metadata else '',
                'subject': reader.metadata.get('/Subject', '') if reader.metadata else '',
                'creator': reader.metadata.get('/Creator', '') if reader.metadata else '',
                'producer': reader.metadata.get('/Producer', '') if reader.metadata else '',
                'total_pages': len(reader.pages)
            }
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    text_content.append({
                        'page': page_num + 1,
                        'text': text.strip(),
                        'bbox': None
                    })
            
            return {
                'text_content': text_content,
                'metadata': metadata,
                'filename': os.path.basename(pdf_path)
            }
    
    def chunk_text(self, text_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split text content into chunks for vector indexing."""
        chunks = []
        
        for page_data in text_content:
            text = page_data['text']
            page_num = page_data['page']
            
            # Split text into sentences first
            sentences = self._split_into_sentences(text)
            
            current_chunk = ""
            chunk_start_sentence = 0
            
            for i, sentence in enumerate(sentences):
                # Check if adding this sentence would exceed chunk size
                if len(current_chunk + sentence) > self.chunk_size and current_chunk:
                    # Save current chunk
                    chunks.append({
                        'text': current_chunk.strip(),
                        'page': page_num,
                        'start_sentence': chunk_start_sentence,
                        'end_sentence': i - 1,
                        'metadata': {
                            'source': page_data.get('filename', ''),
                            'page': page_num
                        }
                    })
                    
                    # Start new chunk with overlap
                    overlap_sentences = sentences[max(0, i - self.chunk_overlap // 50):i]
                    current_chunk = " ".join(overlap_sentences)
                    chunk_start_sentence = max(0, i - self.chunk_overlap // 50)
                
                current_chunk += sentence + " "
            
            # Add final chunk from this page
            if current_chunk.strip():
                chunks.append({
                    'text': current_chunk.strip(),
                    'page': page_num,
                    'start_sentence': chunk_start_sentence,
                    'end_sentence': len(sentences) - 1,
                    'metadata': {
                        'source': page_data.get('filename', ''),
                        'page': page_num
                    }
                })
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences while preserving R code blocks."""
        # Pattern to match R code blocks
        code_pattern = r'```r\s*\n(.*?)\n```'
        
        # Find all code blocks
        code_blocks = re.findall(code_pattern, text, re.DOTALL)
        
        # Replace code blocks with placeholders
        text_with_placeholders = re.sub(code_pattern, 'CODE_BLOCK_PLACEHOLDER', text, flags=re.DOTALL)
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text_with_placeholders)
        
        # Restore code blocks
        code_index = 0
        for i, sentence in enumerate(sentences):
            if 'CODE_BLOCK_PLACEHOLDER' in sentence:
                if code_index < len(code_blocks):
                    sentences[i] = sentence.replace('CODE_BLOCK_PLACEHOLDER', code_blocks[code_index])
                    code_index += 1
        
        return [s.strip() for s in sentences if s.strip()]
    
    def process_pdf_directory(self, pdf_dir: str) -> List[Dict[str, Any]]:
        """Process all PDF files in a directory."""
        pdf_dir = Path(pdf_dir)
        all_chunks = []
        
        if not pdf_dir.exists():
            logger.error(f"PDF directory does not exist: {pdf_dir}")
            return all_chunks
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"Processing {pdf_file.name}")
                extracted_data = self.extract_text_from_pdf(str(pdf_file))
                chunks = self.chunk_text(extracted_data['text_content'])
                
                # Add metadata to each chunk
                for chunk in chunks:
                    chunk['metadata'].update({
                        'title': extracted_data['metadata'].get('title', ''),
                        'author': extracted_data['metadata'].get('author', ''),
                        'subject': extracted_data['metadata'].get('subject', ''),
                        'filename': extracted_data['filename']
                    })
                
                all_chunks.extend(chunks)
                logger.info(f"Created {len(chunks)} chunks from {pdf_file.name}")
                
            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {e}")
                continue
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks
    
    def extract_timestamps(self, text: str) -> List[str]:
        """Extract timestamps from text (e.g., "12:34", "1:23:45")."""
        timestamp_patterns = [
            r'\b\d{1,2}:\d{2}\b',  # MM:SS
            r'\b\d{1,2}:\d{2}:\d{2}\b',  # HH:MM:SS
            r'\b\d{1,2}:\d{2}:\d{2}\.\d{3}\b',  # HH:MM:SS.mmm
        ]
        
        timestamps = []
        for pattern in timestamp_patterns:
            matches = re.findall(pattern, text)
            timestamps.extend(matches)
        
        return timestamps 