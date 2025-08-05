"""
FAISS vector store for efficient similarity search and retrieval of R course materials.
"""

import os
import pickle
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    logging.error(f"FAISS or sentence-transformers not available: {e}")
    raise

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS-based vector store for R course materials."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", index_path: str = "./data/vector_db"):
        self.model_name = model_name
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize the sentence transformer model
        try:
            self.encoder = SentenceTransformer(model_name)
            logger.info(f"Loaded sentence transformer model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load sentence transformer model: {e}")
            raise
        
        # Initialize FAISS index
        self.dimension = self.encoder.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        
        # Store metadata
        self.metadata = []
        self.chunks = []
        
        # Load existing index if available
        self._load_existing_index()
    
    def _load_existing_index(self):
        """Load existing FAISS index and metadata if available."""
        index_file = self.index_path / "faiss_index.bin"
        metadata_file = self.index_path / "metadata.pkl"
        
        if index_file.exists() and metadata_file.exists():
            try:
                # Load FAISS index
                self.index = faiss.read_index(str(index_file))
                
                # Load metadata
                with open(metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                logger.info(f"Loaded existing index with {len(self.metadata)} documents")
                
            except Exception as e:
                logger.error(f"Failed to load existing index: {e}")
                # Reinitialize if loading fails
                self.index = faiss.IndexFlatIP(self.dimension)
                self.metadata = []
    
    def _save_index(self):
        """Save FAISS index and metadata to disk."""
        try:
            # Save FAISS index
            index_file = self.index_path / "faiss_index.bin"
            faiss.write_index(self.index, str(index_file))
            
            # Save metadata
            metadata_file = self.index_path / "metadata.pkl"
            with open(metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            logger.info(f"Saved index with {len(self.metadata)} documents")
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the vector store."""
        if not documents:
            logger.warning("No documents provided to add")
            return
        
        # Extract texts and metadata
        texts = []
        new_metadata = []
        
        for doc in documents:
            text = doc.get('text', '')
            if text.strip():
                texts.append(text)
                new_metadata.append(doc.get('metadata', {}))
        
        if not texts:
            logger.warning("No valid texts found in documents")
            return
        
        # Encode texts to vectors
        logger.info(f"Encoding {len(texts)} documents...")
        embeddings = self.encoder.encode(texts, show_progress_bar=True)
        
        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))
        
        # Store metadata
        self.metadata.extend(new_metadata)
        
        # Save to disk
        self._save_index()
        
        logger.info(f"Added {len(texts)} documents to vector store")
    
    def similarity_search(self, query: str, k: int = 5, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Search for similar documents using cosine similarity."""
        if not query.strip():
            return []
        
        # Encode query
        query_embedding = self.encoder.encode([query])
        
        # Search in FAISS index
        scores, indices = self.index.search(query_embedding.astype('float32'), k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.metadata) and score >= threshold:
                result = {
                    'score': float(score),
                    'metadata': self.metadata[idx].copy(),
                    'index': int(idx)
                }
                results.append(result)
        
        # Sort by score (descending)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def search_with_context(self, query: str, k: int = 5, threshold: float = 0.5) -> Tuple[str, List[Dict[str, Any]]]:
        """Search and return context string with references."""
        results = self.similarity_search(query, k, threshold)
        
        if not results:
            return "", []
        
        # Build context string
        context_parts = []
        references = []
        
        for i, result in enumerate(results):
            metadata = result['metadata']
            score = result['score']
            
            # Extract relevant information
            source = metadata.get('source', 'Unknown Source')
            page = metadata.get('page', '')
            title = metadata.get('title', '')
            
            # Create reference
            ref = {
                'module': title or source,
                'page': str(page) if page else '',
                'score': score,
                'source': source
            }
            references.append(ref)
            
            # Add to context (we'll need to retrieve the actual text)
            context_parts.append(f"[Reference {i+1}] {title} - Page {page} (Relevance: {score:.3f})")
        
        context = "\n".join(context_parts)
        return context, references
    
    def get_document_text(self, index: int) -> Optional[str]:
        """Get the original text for a document index."""
        # This would need to be implemented based on how you store the original texts
        # For now, we'll return None - you might want to store texts separately
        return None
    
    def clear_index(self):
        """Clear the entire index."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        self._save_index()
        logger.info("Cleared vector store index")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            'total_documents': len(self.metadata),
            'index_size': self.index.ntotal,
            'dimension': self.dimension,
            'model_name': self.model_name
        }
    
    def update_documents(self, documents: List[Dict[str, Any]]):
        """Update documents in the vector store (clear and re-add)."""
        logger.info("Updating documents in vector store...")
        self.clear_index()
        self.add_documents(documents)
    
    def batch_similarity_search(self, queries: List[str], k: int = 5) -> List[List[Dict[str, Any]]]:
        """Perform batch similarity search for multiple queries."""
        if not queries:
            return []
        
        # Encode all queries
        query_embeddings = self.encoder.encode(queries)
        
        # Batch search
        scores, indices = self.index.search(query_embeddings.astype('float32'), k)
        
        all_results = []
        for query_scores, query_indices in zip(scores, indices):
            query_results = []
            for score, idx in zip(query_scores, query_indices):
                if idx < len(self.metadata):
                    result = {
                        'score': float(score),
                        'metadata': self.metadata[idx].copy(),
                        'index': int(idx)
                    }
                    query_results.append(result)
            
            # Sort by score
            query_results.sort(key=lambda x: x['score'], reverse=True)
            all_results.append(query_results)
        
        return all_results 