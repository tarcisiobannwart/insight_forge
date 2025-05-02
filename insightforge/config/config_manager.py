"""
Configuration Manager Module
------------------------
Manages configuration settings for the InsightForge application.
"""

import os
import yaml
import json
import logging
from typing import Any, Dict, List, Optional, Union, Tuple, Set
from pathlib import Path

# Setup logger
logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Exception raised for configuration errors."""
    pass


class ConfigManager:
    """
    Manages application configuration from multiple sources.
    
    The ConfigManager loads configuration from:
    1. Default values
    2. Configuration file
    3. Environment variables
    4. Command-line arguments
    
    Each source overrides the previous ones when specified.
    """
    
    # Default configuration
    DEFAULT_CONFIG = {
        # General settings
        "general": {
            "output_dir": "./output",
            "log_level": "INFO",
            "profile": "default"
        },
        
        # Code parsing settings
        "parser": {
            "exclude_dirs": ["venv", "env", ".git", ".github", "node_modules", "__pycache__", ".vscode", ".idea"],
            "exclude_files": ["*.pyc", "*.pyo", "*.pyd", "*.so", "*.dylib", "*.dll", "*.egg-info", "*.egg", "*.whl"],
            "languages": {
                "python": {
                    "enabled": True, 
                    "extensions": [".py"],
                    "detect_docstrings": True,
                    "detect_types": True
                },
                "php": {
                    "enabled": True,
                    "extensions": [".php"],
                    "detect_docstrings": True
                },
                "javascript": {
                    "enabled": False,
                    "extensions": [".js", ".jsx"],
                    "detect_jsdoc": True
                },
                "typescript": {
                    "enabled": False,
                    "extensions": [".ts", ".tsx"],
                    "detect_tsdoc": True
                }
            }
        },
        
        # Documentation generator settings
        "doc_generator": {
            "output_format": "markdown",
            "template_dir": None,  # Use default templates
            "generate_diagrams": True,
            "diagram_format": "mermaid",
            "diagram_types": ["class", "module", "sequence"],
            "index_template": "index.md.j2",
            "include_source_links": True
        },
        
        # Business rules extractor settings
        "business_rules": {
            "enabled": True,
            "extract_from_code": True,
            "extract_from_comments": True,
            "extract_from_docstrings": True,
            "patterns": [
                "Business Rule:",
                "BR:",
                "must",
                "should",
                "required",
                "cannot",
                "must not"
            ]
        },
        
        # Use case extractor settings
        "usecase_extractor": {
            "enabled": True,
            "extract_from_docstrings": True,
            "extract_from_comments": True,
            "extract_from_method_names": True
        },
        
        # Backlog builder settings 
        "backlog_builder": {
            "enabled": True,
            "format": "markdown",
            "include_priority": True,
            "include_story_points": True
        },
        
        # LLM integration settings
        "llm": {
            "enabled": False,
            "provider": "ollama",
            "model": "llama2",
            "endpoint": "http://localhost:11434/api",
            "max_tokens": 1024,
            "temperature": 0.7,
            "embeddings_model": "all-MiniLM-L6-v2"
        }
    }
    
    # Environment variable prefix
    ENV_PREFIX = "INSIGHTFORGE_"
    
    def __init__(self, config_path: Optional[str] = None, 
                 env_prefix: Optional[str] = None,
                 cli_args: Optional[Dict[str, Any]] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file (YAML or JSON)
            env_prefix: Prefix for environment variables
            cli_args: Command-line arguments
        """
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self.config_path = config_path
        self.env_prefix = env_prefix or self.ENV_PREFIX
        self.cli_args = cli_args or {}
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from all sources."""
        # Load from config file
        if self.config_path:
            self._load_from_file(self.config_path)
        else:
            # Try default locations
            for path in self._get_default_config_paths():
                if os.path.exists(path):
                    self._load_from_file(path)
                    break
        
        # Load from environment variables
        self._load_from_env()
        
        # Load from command-line arguments
        self._load_from_cli()
    
    def _get_default_config_paths(self) -> List[str]:
        """Get a list of default configuration file paths to check."""
        paths = []
        
        # Add current directory
        paths.append("./insightforge.yml")
        paths.append("./insightforge.yaml")
        paths.append("./insightforge.json")
        paths.append("./config/insightforge.yml")
        paths.append("./config/insightforge.yaml")
        paths.append("./config/insightforge.json")
        
        # Add user config directory
        user_config_dir = os.path.expanduser("~/.config/insightforge")
        paths.append(os.path.join(user_config_dir, "config.yml"))
        paths.append(os.path.join(user_config_dir, "config.yaml"))
        paths.append(os.path.join(user_config_dir, "config.json"))
        
        # Add system config directory if on Linux/Mac
        if os.name != "nt":  # Not Windows
            paths.append("/etc/insightforge/config.yml")
            paths.append("/etc/insightforge/config.yaml")
            paths.append("/etc/insightforge/config.json")
        
        return paths
    
    def _load_from_file(self, file_path: str) -> None:
        """
        Load configuration from a file.
        
        Args:
            file_path: Path to the configuration file
        
        Raises:
            ConfigError: If the file cannot be loaded
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith(('.yml', '.yaml')):
                    file_config = yaml.safe_load(f)
                elif file_path.endswith('.json'):
                    file_config = json.load(f)
                else:
                    raise ConfigError(f"Unsupported config file format: {file_path}")
                
                if file_config and isinstance(file_config, dict):
                    self._merge_config(file_config)
                    logger.info(f"Loaded configuration from {file_path}")
                    self.config_path = file_path
        except Exception as e:
            logger.warning(f"Failed to load configuration from {file_path}: {str(e)}")
    
    def _load_from_env(self) -> None:
        """
        Load configuration from environment variables.
        
        Environment variables should be in the format:
        INSIGHTFORGE_SECTION_KEY=value
        
        For example:
        INSIGHTFORGE_GENERAL_OUTPUT_DIR=/path/to/output
        """
        prefix_len = len(self.env_prefix)
        env_vars = {k[prefix_len:].lower(): v for k, v in os.environ.items() 
                    if k.startswith(self.env_prefix)}
        
        for key, value in env_vars.items():
            # Split the key into sections (SECTION_KEY_SUBKEY)
            parts = key.split('_')
            if len(parts) >= 2:
                # Convert environment variables to appropriate types
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '', 1).isdigit() and value.count('.') == 1:
                    value = float(value)
                
                # Update config
                self._set_nested_value(parts, value)
    
    def _load_from_cli(self) -> None:
        """
        Load configuration from command-line arguments.
        
        Command-line arguments take precedence over other configuration sources.
        """
        for key, value in self.cli_args.items():
            if value is not None:  # Only override if explicitly provided
                # Convert key from snake_case to nested dict path
                parts = key.split('_')
                if len(parts) >= 1:
                    self._set_nested_value(parts, value)
    
    def _set_nested_value(self, parts: List[str], value: Any) -> None:
        """
        Set a nested value in the configuration dictionary.
        
        Args:
            parts: Path to the configuration option
            value: Value to set
        """
        # Create nested dictionaries if they don't exist
        current = self.config
        for i, part in enumerate(parts[:-1]):
            # Create section if it doesn't exist
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                # Convert to dict if it's not already
                current[part] = {"value": current[part]}
            
            current = current[part]
        
        # Set the final value
        current[parts[-1]] = value
    
    def _merge_config(self, config: Dict[str, Any]) -> None:
        """
        Merge configuration dictionaries.
        
        Args:
            config: Configuration dictionary to merge
        """
        self._merge_dicts(self.config, config)
    
    def _merge_dicts(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively merge source dictionary into target dictionary.
        
        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                self._merge_dicts(target[key], value)
            else:
                # Replace or add the value
                target[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Dot-separated path to the configuration option (e.g., 'general.output_dir')
            default: Default value to return if the key is not found
            
        Returns:
            The configuration value or the default value
        """
        parts = key.split('.')
        current = self.config
        
        for part in parts:
            if part not in current:
                return default
            current = current[part]
        
        return current
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Dot-separated path to the configuration option
            value: Value to set
        """
        parts = key.split('.')
        self._set_nested_value(parts, value)
    
    def as_dict(self) -> Dict[str, Any]:
        """
        Get the entire configuration as a dictionary.
        
        Returns:
            The configuration dictionary
        """
        return self.config.copy()
    
    def save(self, file_path: Optional[str] = None) -> None:
        """
        Save the current configuration to a file.
        
        Args:
            file_path: Path to save the configuration to. If None, uses the original path.
            
        Raises:
            ConfigError: If the configuration could not be saved
        """
        file_path = file_path or self.config_path
        if not file_path:
            raise ConfigError("No configuration file path specified")
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Save configuration
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith(('.yml', '.yaml')):
                    yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
                elif file_path.endswith('.json'):
                    json.dump(self.config, f, indent=2)
                else:
                    raise ConfigError(f"Unsupported config file format: {file_path}")
                
            logger.info(f"Configuration saved to {file_path}")
        except Exception as e:
            raise ConfigError(f"Failed to save configuration to {file_path}: {str(e)}")
    
    def get_profile(self) -> str:
        """
        Get the current profile name.
        
        Returns:
            The current profile name
        """
        return self.get('general.profile', 'default')
    
    def set_profile(self, profile: str) -> None:
        """
        Set the current profile.
        
        Args:
            profile: Profile name
        """
        self.set('general.profile', profile)


def load_config(config_path: Optional[str] = None, 
               env_prefix: Optional[str] = None,
               cli_args: Optional[Dict[str, Any]] = None) -> ConfigManager:
    """
    Load configuration from various sources.
    
    Args:
        config_path: Path to the configuration file
        env_prefix: Prefix for environment variables
        cli_args: Command-line arguments
        
    Returns:
        ConfigManager instance
    """
    return ConfigManager(config_path, env_prefix, cli_args)