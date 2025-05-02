"""
LLM Integration Module
--------------------
Provides integration with various LLM providers for code understanding,
documentation generation, and natural language queries.
"""

from .base import LLMProvider, LLMResponse
from .ollama import OllamaProvider

__all__ = ['LLMProvider', 'LLMResponse', 'OllamaProvider']