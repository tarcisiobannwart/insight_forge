"""
Ollama integration for local LLM inference
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional, Union
import logging
from .base import LLMProvider, LLMResponse


class OllamaAPIError(Exception):
    """Exception raised when there is an error with the Ollama API."""
    pass


class OllamaProvider(LLMProvider):
    """
    Provider for Ollama API integration.
    
    Ollama allows running open-source LLMs locally.
    https://ollama.ai/
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", 
                 model: str = "mistral", 
                 timeout: int = 60):
        """
        Initialize Ollama provider.
        
        Args:
            base_url: Base URL for Ollama API
            model: Default model to use
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to the Ollama API.
        
        Args:
            endpoint: API endpoint
            data: Request data
            
        Returns:
            API response as a dictionary
            
        Raises:
            OllamaAPIError: If the request fails
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Ollama API error: {str(e)}")
            raise OllamaAPIError(f"Ollama API error: {str(e)}")
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Generate text using Ollama.
        
        Args:
            prompt: The prompt to send to the model
            **kwargs: Additional parameters to pass to the model
                - model: Override the default model
                - temperature: Control randomness (default: 0.7)
                - top_p: Top probability mass to consider (default: 0.9)
                - max_tokens: Maximum tokens to generate (default: 1000)
            
        Returns:
            LLMResponse: The response from the model
        """
        model = kwargs.get('model', self.model)
        data = {
            'model': model,
            'prompt': prompt,
            'options': {
                'temperature': kwargs.get('temperature', 0.7),
                'top_p': kwargs.get('top_p', 0.9),
                'num_predict': kwargs.get('max_tokens', 1000),
                'stop': kwargs.get('stop', []),
            }
        }
        
        try:
            response = self._make_request("api/generate", data)
            
            # Calculate token usage (approximate since Ollama doesn't provide this directly)
            # Roughly 4 chars per token as a simple approximation
            input_tokens = len(prompt) // 4
            output_tokens = len(response.get('response', '')) // 4
            
            return LLMResponse(
                content=response.get('response', ''),
                model=model,
                usage={
                    'prompt_tokens': input_tokens,
                    'completion_tokens': output_tokens,
                    'total_tokens': input_tokens + output_tokens
                },
                raw_response=response
            )
        except OllamaAPIError as e:
            self.logger.error(f"Error generating text: {str(e)}")
            # Return an empty response on error
            return LLMResponse(
                content=f"Error: {str(e)}",
                model=model,
                usage={'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
            )
    
    def generate_chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """
        Generate a chat response using Ollama.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            **kwargs: Additional parameters to pass to the model
                - model: Override the default model
                - temperature: Control randomness (default: 0.7)
                - top_p: Top probability mass to consider (default: 0.9)
                - max_tokens: Maximum tokens to generate (default: 1000)
            
        Returns:
            LLMResponse: The response from the model
        """
        model = kwargs.get('model', self.model)
        data = {
            'model': model,
            'messages': messages,
            'options': {
                'temperature': kwargs.get('temperature', 0.7),
                'top_p': kwargs.get('top_p', 0.9),
                'num_predict': kwargs.get('max_tokens', 1000),
                'stop': kwargs.get('stop', []),
            }
        }
        
        try:
            response = self._make_request("api/chat", data)
            
            # Calculate token usage (approximate)
            input_tokens = sum(len(m.get('content', '')) for m in messages) // 4
            output_tokens = len(response.get('message', {}).get('content', '')) // 4
            
            return LLMResponse(
                content=response.get('message', {}).get('content', ''),
                model=model,
                usage={
                    'prompt_tokens': input_tokens,
                    'completion_tokens': output_tokens,
                    'total_tokens': input_tokens + output_tokens
                },
                raw_response=response
            )
        except OllamaAPIError as e:
            self.logger.error(f"Error generating chat response: {str(e)}")
            # Return an empty response on error
            return LLMResponse(
                content=f"Error: {str(e)}",
                model=model,
                usage={'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
            )
    
    def get_embeddings(self, text: Union[str, List[str]], **kwargs) -> List[List[float]]:
        """
        Get vector embeddings for text using Ollama.
        
        Args:
            text: Text or list of texts to get embeddings for
            **kwargs: Additional parameters
                - model: Override the default model
                
        Returns:
            List of embedding vectors
        """
        model = kwargs.get('model', self.model)
        
        # Handle single text or list of texts
        texts = [text] if isinstance(text, str) else text
        embeddings = []
        
        for t in texts:
            data = {
                'model': model,
                'prompt': t,
            }
            
            try:
                response = self._make_request("api/embeddings", data)
                embedding = response.get('embedding', [])
                embeddings.append(embedding)
            except OllamaAPIError as e:
                self.logger.error(f"Error getting embeddings: {str(e)}")
                # Return an empty embedding on error
                embeddings.append([])
        
        return embeddings
    
    def list_models(self) -> List[str]:
        """
        List available models in Ollama.
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        except requests.RequestException as e:
            self.logger.error(f"Error listing models: {str(e)}")
            return []