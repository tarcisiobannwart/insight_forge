"""
Embeddings and vector search module for code understanding.
"""

import os
import json
import pickle
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from pathlib import Path
import logging
from .base import LLMProvider


class EmbeddingStore:
    """
    Store and retrieve vector embeddings for semantic search.
    """
    
    def __init__(self, data_dir: str, provider: LLMProvider):
        """
        Initialize the embedding store.
        
        Args:
            data_dir: Directory to store embeddings
            provider: LLM provider to use for generating embeddings
        """
        self.data_dir = data_dir
        self.provider = provider
        self.embeddings = {}
        self.metadata = {}
        self.logger = logging.getLogger(__name__)
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # File paths for embeddings and metadata
        self.embeddings_file = os.path.join(data_dir, "embeddings.pkl")
        self.metadata_file = os.path.join(data_dir, "metadata.json")
        
        # Load existing embeddings if available
        self._load_data()
    
    def _load_data(self) -> None:
        """Load embeddings and metadata from files."""
        # Load embeddings
        if os.path.exists(self.embeddings_file):
            try:
                with open(self.embeddings_file, 'rb') as f:
                    self.embeddings = pickle.load(f)
                self.logger.info(f"Loaded {len(self.embeddings)} embeddings from {self.embeddings_file}")
            except Exception as e:
                self.logger.error(f"Error loading embeddings: {str(e)}")
        
        # Load metadata
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                self.logger.info(f"Loaded metadata from {self.metadata_file}")
            except Exception as e:
                self.logger.error(f"Error loading metadata: {str(e)}")
    
    def _save_data(self) -> None:
        """Save embeddings and metadata to files."""
        # Save embeddings
        try:
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(self.embeddings, f)
            self.logger.info(f"Saved {len(self.embeddings)} embeddings to {self.embeddings_file}")
        except Exception as e:
            self.logger.error(f"Error saving embeddings: {str(e)}")
        
        # Save metadata
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
            self.logger.info(f"Saved metadata to {self.metadata_file}")
        except Exception as e:
            self.logger.error(f"Error saving metadata: {str(e)}")
    
    def add_embedding(self, key: str, text: str, metadata: Dict[str, Any] = None) -> None:
        """
        Add a text embedding to the store.
        
        Args:
            key: Unique identifier for the text
            text: Text to embed
            metadata: Additional metadata to store
        """
        # Generate embedding using the provider
        embeddings = self.provider.get_embeddings(text)
        
        if embeddings and len(embeddings) > 0 and len(embeddings[0]) > 0:
            self.embeddings[key] = embeddings[0]
            self.metadata[key] = {
                'text': text,
                'metadata': metadata or {}
            }
            self.logger.debug(f"Added embedding for key: {key}")
        else:
            self.logger.warning(f"Failed to generate embedding for key: {key}")
    
    def add_code_embedding(self, file_path: str, code: str, 
                          metadata: Dict[str, Any] = None) -> None:
        """
        Add a code embedding to the store.
        
        Args:
            file_path: Path to the code file (used as key)
            code: Code text to embed
            metadata: Additional metadata like language, classes, functions
        """
        key = f"code:{file_path}"
        meta = metadata or {}
        meta['type'] = 'code'
        meta['file_path'] = file_path
        self.add_embedding(key, code, meta)
    
    def add_class_embedding(self, class_name: str, file_path: str, 
                           code: str, docstring: str,
                           metadata: Dict[str, Any] = None) -> None:
        """
        Add a class embedding to the store.
        
        Args:
            class_name: Name of the class
            file_path: Path to the file containing the class
            code: Class code text
            docstring: Class docstring
            metadata: Additional metadata
        """
        key = f"class:{file_path}:{class_name}"
        
        # Create a rich representation for the embedding
        text = f"Class: {class_name}\n\nDocstring: {docstring or 'No docstring'}\n\nCode:\n{code}"
        
        meta = metadata or {}
        meta.update({
            'type': 'class',
            'name': class_name,
            'file_path': file_path,
            'docstring': docstring
        })
        
        self.add_embedding(key, text, meta)
    
    def add_function_embedding(self, function_name: str, file_path: str,
                              code: str, docstring: str,
                              metadata: Dict[str, Any] = None) -> None:
        """
        Add a function embedding to the store.
        
        Args:
            function_name: Name of the function
            file_path: Path to the file containing the function
            code: Function code text
            docstring: Function docstring
            metadata: Additional metadata
        """
        key = f"function:{file_path}:{function_name}"
        
        # Create a rich representation for the embedding
        text = f"Function: {function_name}\n\nDocstring: {docstring or 'No docstring'}\n\nCode:\n{code}"
        
        meta = metadata or {}
        meta.update({
            'type': 'function',
            'name': function_name,
            'file_path': file_path,
            'docstring': docstring
        })
        
        self.add_embedding(key, text, meta)
    
    def add_doc_embedding(self, doc_path: str, content: str,
                         metadata: Dict[str, Any] = None) -> None:
        """
        Add a documentation embedding to the store.
        
        Args:
            doc_path: Path to the documentation file
            content: Document content
            metadata: Additional metadata
        """
        key = f"doc:{doc_path}"
        
        meta = metadata or {}
        meta.update({
            'type': 'doc',
            'file_path': doc_path
        })
        
        self.add_embedding(key, content, meta)
    
    def search(self, query: str, top_k: int = 5, 
              filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None) -> List[Dict[str, Any]]:
        """
        Search embeddings by semantic similarity.
        
        Args:
            query: Query text
            top_k: Number of results to return
            filter_fn: Optional function to filter results by metadata
            
        Returns:
            List of results with metadata and similarity score
        """
        if not self.embeddings:
            self.logger.warning("No embeddings available for search")
            return []
        
        # Get query embedding
        query_embedding = self.provider.get_embeddings(query)
        if not query_embedding or not query_embedding[0]:
            self.logger.error("Failed to generate embedding for query")
            return []
        
        query_vector = np.array(query_embedding[0])
        results = []
        
        # Calculate cosine similarity for all embeddings
        for key, embedding in self.embeddings.items():
            if key not in self.metadata:
                continue
                
            vector = np.array(embedding)
            
            # Calculate cosine similarity
            similarity = np.dot(query_vector, vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(vector)
            )
            
            metadata = self.metadata[key]
            
            # Apply filter if provided
            if filter_fn and not filter_fn(metadata.get('metadata', {})):
                continue
            
            results.append({
                'key': key,
                'similarity': float(similarity),
                'text': metadata.get('text', ''),
                'metadata': metadata.get('metadata', {})
            })
        
        # Sort by similarity (highest first) and return top_k results
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def search_code(self, query: str, top_k: int = 5, 
                   language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search code by semantic similarity.
        
        Args:
            query: Query text
            top_k: Number of results to return
            language: Optional language filter
            
        Returns:
            List of code results with metadata and similarity score
        """
        def code_filter(metadata):
            if metadata.get('type') != 'code':
                return False
            if language and metadata.get('language') != language:
                return False
            return True
        
        return self.search(query, top_k, code_filter)
    
    def search_classes(self, query: str, top_k: int = 5,
                      language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search classes by semantic similarity.
        
        Args:
            query: Query text
            top_k: Number of results to return
            language: Optional language filter
            
        Returns:
            List of class results with metadata and similarity score
        """
        def class_filter(metadata):
            if metadata.get('type') != 'class':
                return False
            if language and metadata.get('language') != language:
                return False
            return True
        
        return self.search(query, top_k, class_filter)
    
    def search_functions(self, query: str, top_k: int = 5,
                        language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search functions by semantic similarity.
        
        Args:
            query: Query text
            top_k: Number of results to return
            language: Optional language filter
            
        Returns:
            List of function results with metadata and similarity score
        """
        def function_filter(metadata):
            if metadata.get('type') != 'function':
                return False
            if language and metadata.get('language') != language:
                return False
            return True
        
        return self.search(query, top_k, function_filter)
    
    def search_docs(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search documentation by semantic similarity.
        
        Args:
            query: Query text
            top_k: Number of results to return
            
        Returns:
            List of documentation results with metadata and similarity score
        """
        def doc_filter(metadata):
            return metadata.get('type') == 'doc'
        
        return self.search(query, top_k, doc_filter)
    
    def clear(self) -> None:
        """Clear all embeddings and metadata."""
        self.embeddings = {}
        self.metadata = {}
        
        # Remove files
        if os.path.exists(self.embeddings_file):
            os.remove(self.embeddings_file)
        if os.path.exists(self.metadata_file):
            os.remove(self.metadata_file)
        
        self.logger.info("Cleared all embeddings and metadata")
    
    def save(self) -> None:
        """Save embeddings and metadata to disk."""
        self._save_data()


class CodeEmbedder:
    """
    Create embeddings for an entire codebase.
    """
    
    def __init__(self, project_path: str, data_dir: str, provider: LLMProvider):
        """
        Initialize the code embedder.
        
        Args:
            project_path: Path to the project directory
            data_dir: Directory to store embeddings
            provider: LLM provider to use for generating embeddings
        """
        self.project_path = project_path
        self.embedding_store = EmbeddingStore(data_dir, provider)
        self.logger = logging.getLogger(__name__)
    
    def embed_codebase(self, parsed_data: Dict[str, Any]) -> None:
        """
        Create embeddings for the entire codebase.
        
        Args:
            parsed_data: Parsed code data from CodeParser
        """
        self.logger.info(f"Creating embeddings for codebase: {self.project_path}")
        
        # Embed classes
        for class_data in parsed_data.get('classes', []):
            file_path = class_data.get('file_path', '')
            class_name = class_data.get('name', '')
            docstring = class_data.get('docstring', '')
            
            # We don't have the actual code text, so we'll create a representation
            # from the available data
            methods_text = "\n".join([
                f"Method: {m.get('name')}({', '.join(m.get('parameters', []))})" +
                (f"\n{m.get('docstring')}" if m.get('docstring') else "")
                for m in class_data.get('methods', [])
            ])
            
            code_repr = f"Class {class_name}:\n" + \
                       (f"Docstring: {docstring}\n\n" if docstring else "") + \
                       f"Methods:\n{methods_text}\n\n"
            
            # Determine language from file extension
            language = Path(file_path).suffix.lstrip('.') if file_path else None
            
            # Add embedding
            self.embedding_store.add_class_embedding(
                class_name=class_name,
                file_path=file_path,
                code=code_repr,
                docstring=docstring,
                metadata={
                    'language': language,
                    'base_classes': class_data.get('base_classes', []),
                    'methods': [m.get('name') for m in class_data.get('methods', [])]
                }
            )
            
            self.logger.debug(f"Created embedding for class: {class_name}")
        
        # Embed functions
        for func_data in parsed_data.get('functions', []):
            file_path = func_data.get('file_path', '')
            func_name = func_data.get('name', '')
            docstring = func_data.get('docstring', '')
            
            # Create function representation
            params_text = ", ".join(func_data.get('parameters', []))
            code_repr = f"Function {func_name}({params_text}):\n" + \
                       (f"Docstring: {docstring}\n\n" if docstring else "")
            
            # Determine language from file extension
            language = Path(file_path).suffix.lstrip('.') if file_path else None
            
            # Add embedding
            self.embedding_store.add_function_embedding(
                function_name=func_name,
                file_path=file_path,
                code=code_repr,
                docstring=docstring,
                metadata={
                    'language': language,
                    'parameters': func_data.get('parameters', []),
                    'return_type': func_data.get('return_type')
                }
            )
            
            self.logger.debug(f"Created embedding for function: {func_name}")
        
        # Save embeddings
        self.embedding_store.save()
        self.logger.info(f"Embeddings created and saved for codebase: {self.project_path}")
    
    def embed_documentation(self, docs_dir: str) -> None:
        """
        Create embeddings for documentation files.
        
        Args:
            docs_dir: Directory containing documentation files
        """
        self.logger.info(f"Creating embeddings for documentation in: {docs_dir}")
        
        # Find markdown files
        for root, _, files in os.walk(docs_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.project_path)
                    
                    # Read file content
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Add embedding
                        self.embedding_store.add_doc_embedding(
                            doc_path=rel_path,
                            content=content,
                            metadata={
                                'title': self._extract_title(content),
                                'file_name': file,
                                'full_path': file_path
                            }
                        )
                        
                        self.logger.debug(f"Created embedding for doc: {rel_path}")
                    except Exception as e:
                        self.logger.error(f"Error embedding doc {file_path}: {str(e)}")
        
        # Save embeddings
        self.embedding_store.save()
        self.logger.info(f"Embeddings created and saved for documentation in: {docs_dir}")
    
    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content."""
        lines = content.strip().split('\n')
        for line in lines:
            if line.startswith('# '):
                return line.replace('# ', '')
        return "Untitled Document"