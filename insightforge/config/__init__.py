"""
Configuration Module
------------------
Handles loading, validating, and providing application configuration.

This module provides a centralized configuration system for InsightForge.
It supports loading configuration from YAML files, environment variables,
and command-line arguments, with appropriate precedence.
"""

from .config_manager import ConfigManager, load_config

__all__ = ['ConfigManager', 'load_config']