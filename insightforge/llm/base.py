"""
Base classes for LLM integration
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union


@dataclass
class LLMResponse:
    """Represents a response from an LLM model."""
    content: str
    model: str
    usage: Dict[str, int]
    raw_response: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Generate text using the LLM model.
        
        Args:
            prompt: The prompt to send to the model
            **kwargs: Additional parameters to pass to the model
            
        Returns:
            LLMResponse: The response from the model
        """
        pass
    
    @abstractmethod
    def generate_chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """
        Generate a chat response using the LLM model.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            **kwargs: Additional parameters to pass to the model
            
        Returns:
            LLMResponse: The response from the model
        """
        pass
    
    @abstractmethod
    def get_embeddings(self, text: Union[str, List[str]], **kwargs) -> List[List[float]]:
        """
        Get vector embeddings for text.
        
        Args:
            text: Text or list of texts to get embeddings for
            **kwargs: Additional parameters
            
        Returns:
            List of embedding vectors
        """
        pass