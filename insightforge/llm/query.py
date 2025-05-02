"""
Natural language query interface for code understanding.
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from .base import LLMProvider, LLMResponse
from .embeddings import EmbeddingStore


class QueryResult:
    """Represents the result of a natural language query."""
    
    def __init__(self, 
                answer: str,
                sources: List[Dict[str, Any]] = None,
                raw_response: Any = None):
        """
        Initialize a query result.
        
        Args:
            answer: The answer text
            sources: Source references for the answer
            raw_response: Raw LLM response data
        """
        self.answer = answer
        self.sources = sources or []
        self.raw_response = raw_response
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'answer': self.answer,
            'sources': self.sources
        }
    
    def format_markdown(self) -> str:
        """Format the result as markdown."""
        md = f"# Answer\n\n{self.answer}\n\n"
        
        if self.sources:
            md += "## Sources\n\n"
            for i, source in enumerate(self.sources):
                md += f"### Source {i+1}\n\n"
                
                # Add metadata based on type
                source_type = source.get('metadata', {}).get('type')
                if source_type == 'class':
                    class_name = source.get('metadata', {}).get('name', 'Unknown Class')
                    file_path = source.get('metadata', {}).get('file_path', 'Unknown file')
                    md += f"**Class**: {class_name}  \n"
                    md += f"**File**: {file_path}  \n"
                    md += f"**Similarity**: {source.get('similarity', 0):.2f}  \n\n"
                    
                    # Add class docstring if available
                    docstring = source.get('metadata', {}).get('docstring')
                    if docstring:
                        md += f"**Docstring**:  \n{docstring}\n\n"
                
                elif source_type == 'function':
                    func_name = source.get('metadata', {}).get('name', 'Unknown Function')
                    file_path = source.get('metadata', {}).get('file_path', 'Unknown file')
                    md += f"**Function**: {func_name}  \n"
                    md += f"**File**: {file_path}  \n"
                    md += f"**Similarity**: {source.get('similarity', 0):.2f}  \n\n"
                    
                    # Add function docstring if available
                    docstring = source.get('metadata', {}).get('docstring')
                    if docstring:
                        md += f"**Docstring**:  \n{docstring}\n\n"
                
                elif source_type == 'doc':
                    doc_path = source.get('metadata', {}).get('file_path', 'Unknown document')
                    title = source.get('metadata', {}).get('title', 'Untitled Document')
                    md += f"**Document**: {title}  \n"
                    md += f"**Path**: {doc_path}  \n"
                    md += f"**Similarity**: {source.get('similarity', 0):.2f}  \n\n"
                
                else:
                    # Generic source
                    md += f"**Similarity**: {source.get('similarity', 0):.2f}  \n\n"
                    
                # Add a preview of the text
                text = source.get('text', '')
                preview = text[:500] + "..." if len(text) > 500 else text
                md += f"```\n{preview}\n```\n\n"
        
        return md


class QueryEngine:
    """
    Natural language query engine for code understanding.
    """
    
    def __init__(self, provider: LLMProvider, embedding_store: EmbeddingStore):
        """
        Initialize the query engine.
        
        Args:
            provider: LLM provider for answering questions
            embedding_store: Store of code embeddings
        """
        self.provider = provider
        self.embedding_store = embedding_store
        self.logger = logging.getLogger(__name__)
    
    def query(self, question: str, max_sources: int = 5) -> QueryResult:
        """
        Answer a natural language question about code.
        
        Args:
            question: The question to answer
            max_sources: Maximum number of sources to retrieve
            
        Returns:
            QueryResult containing the answer and sources
        """
        self.logger.info(f"Processing query: {question}")
        
        # Search for relevant code
        code_results = self.embedding_store.search(question, top_k=max_sources)
        
        if not code_results:
            self.logger.warning("No relevant code found for the query")
            return QueryResult(
                answer="I couldn't find any relevant code to answer your question."
            )
        
        # Create context for the LLM
        context = self._create_context(question, code_results)
        
        # Generate answer using the LLM
        response = self.provider.generate(context)
        
        # Create result
        return QueryResult(
            answer=response.content,
            sources=code_results,
            raw_response=response.raw_response
        )
    
    def _create_context(self, question: str, sources: List[Dict[str, Any]]) -> str:
        """
        Create a context for the LLM to answer the question.
        
        Args:
            question: The question to answer
            sources: Relevant sources from embedding search
            
        Returns:
            Context prompt for the LLM
        """
        context = "You are an expert code assistant that helps developers understand their codebase. "
        context += "Answer the following question based on the code snippets provided.\n\n"
        
        context += f"Question: {question}\n\n"
        
        context += "Relevant code:\n\n"
        
        for i, source in enumerate(sources):
            source_type = source.get('metadata', {}).get('type', 'unknown')
            
            if source_type == 'class':
                class_name = source.get('metadata', {}).get('name', 'Unknown Class')
                file_path = source.get('metadata', {}).get('file_path', 'Unknown file')
                context += f"[Source {i+1}] Class: {class_name} (File: {file_path})\n"
                
                # Add docstring if available
                docstring = source.get('metadata', {}).get('docstring')
                if docstring:
                    context += f"Docstring: {docstring}\n"
                
                # Add sample from the text
                text = source.get('text', '')
                context += f"{text[:1000]}...\n\n" if len(text) > 1000 else f"{text}\n\n"
            
            elif source_type == 'function':
                func_name = source.get('metadata', {}).get('name', 'Unknown Function')
                file_path = source.get('metadata', {}).get('file_path', 'Unknown file')
                context += f"[Source {i+1}] Function: {func_name} (File: {file_path})\n"
                
                # Add docstring if available
                docstring = source.get('metadata', {}).get('docstring')
                if docstring:
                    context += f"Docstring: {docstring}\n"
                
                # Add sample from the text
                text = source.get('text', '')
                context += f"{text[:1000]}...\n\n" if len(text) > 1000 else f"{text}\n\n"
            
            elif source_type == 'doc':
                doc_path = source.get('metadata', {}).get('file_path', 'Unknown document')
                title = source.get('metadata', {}).get('title', 'Untitled Document')
                context += f"[Source {i+1}] Document: {title} (Path: {doc_path})\n"
                
                # Add sample from the text
                text = source.get('text', '')
                context += f"{text[:1000]}...\n\n" if len(text) > 1000 else f"{text}\n\n"
            
            else:
                # Generic source
                context += f"[Source {i+1}] Unknown type\n"
                text = source.get('text', '')
                context += f"{text[:1000]}...\n\n" if len(text) > 1000 else f"{text}\n\n"
        
        context += "Please answer the question based on the provided code snippets. "
        context += "If you can't answer the question with the given information, say so. "
        context += "Focus on providing accurate and helpful information for understanding the code."
        
        return context
    
    def explain_code(self, code: str) -> QueryResult:
        """
        Explain a code snippet.
        
        Args:
            code: The code to explain
            
        Returns:
            QueryResult containing the explanation
        """
        self.logger.info("Processing code explanation request")
        
        prompt = "You are an expert code explainer. Provide a clear and detailed explanation of the following code:\n\n"
        prompt += f"```\n{code}\n```\n\n"
        prompt += "Please include:\n"
        prompt += "1. A high-level overview of what the code does\n"
        prompt += "2. Explanation of key components and their purpose\n"
        prompt += "3. Any potential issues or improvements\n"
        
        response = self.provider.generate(prompt)
        
        return QueryResult(
            answer=response.content,
            raw_response=response.raw_response
        )
    
    def suggest_improvements(self, code: str) -> QueryResult:
        """
        Suggest improvements for a code snippet.
        
        Args:
            code: The code to improve
            
        Returns:
            QueryResult containing suggestions
        """
        self.logger.info("Processing code improvement request")
        
        prompt = "You are an expert code reviewer. Suggest improvements for the following code:\n\n"
        prompt += f"```\n{code}\n```\n\n"
        prompt += "Please include:\n"
        prompt += "1. Potential bugs or edge cases\n"
        prompt += "2. Performance optimizations\n"
        prompt += "3. Code style and readability improvements\n"
        prompt += "4. Best practices that could be applied\n"
        prompt += "5. Specific code changes to implement these improvements\n"
        
        response = self.provider.generate(prompt)
        
        return QueryResult(
            answer=response.content,
            raw_response=response.raw_response
        )
    
    def generate_docstring(self, code: str, language: str = "python") -> QueryResult:
        """
        Generate a docstring for a code snippet.
        
        Args:
            code: The code to document
            language: Programming language of the code
            
        Returns:
            QueryResult containing the generated docstring
        """
        self.logger.info(f"Generating docstring for {language} code")
        
        prompt = f"You are an expert {language} developer. Generate a comprehensive docstring "
        prompt += f"for the following {language} code using the standard docstring format for {language}:\n\n"
        prompt += f"```{language}\n{code}\n```\n\n"
        prompt += "Include:\n"
        prompt += "1. A clear description of what the code does\n"
        prompt += "2. Parameters with types and descriptions\n"
        prompt += "3. Return values with types and descriptions\n"
        prompt += "4. Exceptions that might be raised\n"
        prompt += "5. Examples of usage if appropriate\n"
        
        response = self.provider.generate(prompt)
        
        return QueryResult(
            answer=response.content,
            raw_response=response.raw_response
        )