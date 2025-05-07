"""
Advanced Configuration Manager for InsightForge

This module provides an extended configuration management system with support
for credentials, profiles, and specialized LLM configurations.
"""

import os
import yaml
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path

from .config_manager import ConfigManager
from .credentials_manager import get_credentials_manager

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for a specific LLM model."""
    
    id: str
    display_name: Optional[str] = None
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    default_for: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider with multiple models."""
    
    name: str
    type: str
    default: bool = False
    models: List[ModelConfig] = field(default_factory=list)
    
    @property
    def default_model(self) -> Optional[ModelConfig]:
        """Get the default model for this provider."""
        if not self.models:
            return None
        
        # First look for a model marked as default for general use
        for model in self.models:
            if "default" in model.default_for:
                return model
        
        # Otherwise, return the first model
        return self.models[0]
    
    def get_model_for_task(self, task: str) -> Optional[ModelConfig]:
        """
        Get the model configured for a specific task.
        
        Args:
            task: Task name (e.g., 'code_analysis', 'documentation')
            
        Returns:
            The model configuration or None if not found
        """
        for model in self.models:
            if task in model.default_for:
                return model
        
        # Fall back to default model
        return self.default_model


@dataclass
class IntegrationConfig:
    """Configuration for an external integration (e.g., Jira, GitHub)."""
    
    name: str
    enabled: bool = False
    settings: Dict[str, Any] = field(default_factory=dict)
    credentials: Dict[str, str] = field(default_factory=dict)


class AdvancedConfigManager(ConfigManager):
    """
    Advanced configuration manager with support for credentials and profiles.
    
    Extends the base ConfigManager with additional functionality for managing
    LLM providers, models, and integration settings.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the advanced configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        super().__init__(config_file)
        self.credentials_manager = get_credentials_manager()
        
        # Ensure advanced sections exist
        self._ensure_advanced_structure()
    
    def _ensure_advanced_structure(self) -> None:
        """Ensure that all required advanced sections exist in the configuration."""
        if 'project' not in self.config:
            self.config['project'] = {
                'name': 'Project',
                'description': '',
                'version': '1.0.0',
                'paths': {}
            }
        
        if 'llm_providers' not in self.config:
            self.config['llm_providers'] = []
        
        if 'integrations' not in self.config:
            self.config['integrations'] = {}
    
    def get_secure_config(self) -> Dict[str, Any]:
        """
        Get a secure copy of the configuration with sensitive data masked.
        
        Returns:
            Configuration dictionary with sensitive data masked
        """
        import copy
        secure_config = copy.deepcopy(self.config)
        
        # Mask credentials in LLM providers
        if 'llm_providers' in secure_config:
            for provider in secure_config['llm_providers']:
                if 'models' in provider:
                    for model in provider['models']:
                        if 'api_key' in model and model['api_key']:
                            model['api_key'] = "<CREDENTIAL_PLACEHOLDER>"
        
        # Mask credentials in integrations
        if 'integrations' in secure_config:
            for integration_name, integration in secure_config['integrations'].items():
                if 'credentials' in integration:
                    for key in integration['credentials']:
                        integration['credentials'][key] = "<CREDENTIAL_PLACEHOLDER>"
        
        return secure_config
    
    def get_llm_providers(self) -> List[ProviderConfig]:
        """
        Get all configured LLM providers.
        
        Returns:
            List of provider configurations
        """
        providers = []
        
        for provider_data in self.config.get('llm_providers', []):
            models = []
            
            for model_data in provider_data.get('models', []):
                # Check if API key is a placeholder and retrieve from credentials manager
                api_key = model_data.get('api_key')
                if api_key == "<CREDENTIAL_PLACEHOLDER>":
                    provider_name = provider_data.get('name')
                    model_id = model_data.get('id')
                    api_key = self.credentials_manager.get_credential(
                        f"llm_{provider_name}", f"model_{model_id}_api_key"
                    )
                
                models.append(ModelConfig(
                    id=model_data.get('id'),
                    display_name=model_data.get('display_name'),
                    api_key=api_key,
                    endpoint=model_data.get('endpoint'),
                    default_for=model_data.get('default_for', []),
                    parameters=model_data.get('parameters', {})
                ))
            
            providers.append(ProviderConfig(
                name=provider_data.get('name'),
                type=provider_data.get('type'),
                default=provider_data.get('default', False),
                models=models
            ))
        
        return providers
    
    def get_default_provider(self) -> Optional[ProviderConfig]:
        """
        Get the default LLM provider.
        
        Returns:
            Default provider configuration or None if not found
        """
        providers = self.get_llm_providers()
        
        # First try to find explicitly marked default provider
        for provider in providers:
            if provider.default:
                return provider
        
        # Otherwise, return the first provider if any
        if providers:
            return providers[0]
        
        return None
    
    def add_llm_provider(self, provider: ProviderConfig) -> None:
        """
        Add or update an LLM provider.
        
        Args:
            provider: Provider configuration
        """
        # Prepare provider data structure
        provider_data = {
            'name': provider.name,
            'type': provider.type,
            'default': provider.default,
            'models': []
        }
        
        # Add models
        for model in provider.models:
            # Store API key in credentials manager if available
            if model.api_key:
                self.credentials_manager.set_credential(
                    f"llm_{provider.name}", f"model_{model.id}_api_key", model.api_key
                )
                api_key_value = "<CREDENTIAL_PLACEHOLDER>"
            else:
                api_key_value = None
            
            model_data = {
                'id': model.id,
                'display_name': model.display_name,
                'api_key': api_key_value,
                'endpoint': model.endpoint,
                'default_for': model.default_for,
                'parameters': model.parameters
            }
            
            provider_data['models'].append(model_data)
        
        # Check if provider already exists
        existing_providers = self.config.get('llm_providers', [])
        for i, existing in enumerate(existing_providers):
            if existing.get('name') == provider.name:
                # Update existing provider
                existing_providers[i] = provider_data
                self.config['llm_providers'] = existing_providers
                return
        
        # Add new provider
        existing_providers.append(provider_data)
        self.config['llm_providers'] = existing_providers
        
        # If this is the first provider or marked as default, ensure it's the only default
        if provider.default or len(existing_providers) == 1:
            self._ensure_single_default_provider(provider.name)
    
    def _ensure_single_default_provider(self, default_name: str) -> None:
        """
        Ensure only one provider is marked as default.
        
        Args:
            default_name: Name of the provider to set as default
        """
        providers = self.config.get('llm_providers', [])
        for provider in providers:
            provider['default'] = (provider.get('name') == default_name)
    
    def get_integrations(self) -> Dict[str, IntegrationConfig]:
        """
        Get all configured external integrations.
        
        Returns:
            Dictionary of integration configurations by name
        """
        integrations = {}
        
        for name, data in self.config.get('integrations', {}).items():
            # Check credentials and mark integration as enabled if credentials exist
            credentials = {}
            enabled = data.get('enabled', False)
            
            if 'credentials' in data:
                for key, value in data['credentials'].items():
                    if value == "<CREDENTIAL_PLACEHOLDER>":
                        # Retrieve from credentials manager
                        actual_value = self.credentials_manager.get_credential(name, key)
                        credentials[key] = actual_value
                        
                        # Mark as enabled if we have all required credentials
                        if actual_value:
                            required_creds_exist = True
                            for req_key in data['credentials']:
                                if req_key != key and not credentials.get(req_key):
                                    required_creds_exist = False
                                    break
                            
                            if required_creds_exist:
                                enabled = True
                    else:
                        credentials[key] = value
            
            integrations[name] = IntegrationConfig(
                name=name,
                enabled=enabled,
                settings=data.get('settings', {}),
                credentials=credentials
            )
        
        return integrations
    
    def update_integration(self, name: str, settings: Dict[str, Any], 
                          credentials: Dict[str, str]) -> None:
        """
        Update an integration configuration.
        
        Args:
            name: Integration name
            settings: Integration settings
            credentials: Integration credentials
        """
        # Initialize integrations section if it doesn't exist
        if 'integrations' not in self.config:
            self.config['integrations'] = {}
        
        # Initialize integration if it doesn't exist
        if name not in self.config['integrations']:
            self.config['integrations'][name] = {
                'enabled': False,
                'settings': {},
                'credentials': {}
            }
        
        # Update settings
        self.config['integrations'][name]['settings'] = settings
        
        # Update credentials
        for key, value in credentials.items():
            # Skip placeholder values
            if value == "<CREDENTIAL_PLACEHOLDER>":
                continue
            
            # Store actual values in credentials manager and use placeholder in config
            if value:
                self.credentials_manager.set_credential(name, key, value)
                self.config['integrations'][name]['credentials'][key] = "<CREDENTIAL_PLACEHOLDER>"
            else:
                # Remove credential if value is empty
                self.credentials_manager.delete_credential(name, key)
                if key in self.config['integrations'][name]['credentials']:
                    del self.config['integrations'][name]['credentials'][key]
        
        # Mark as enabled if we have all required credentials
        self.config['integrations'][name]['enabled'] = self._check_integration_enabled(name)
    
    def _check_integration_enabled(self, name: str) -> bool:
        """
        Check if an integration is properly configured and should be enabled.
        
        Args:
            name: Integration name
            
        Returns:
            True if the integration is properly configured
        """
        if name not in self.config.get('integrations', {}):
            return False
        
        # Check required settings based on integration type
        integration = self.config['integrations'][name]
        
        if name == 'jira':
            # Jira requires URL, project key, and credentials
            settings = integration.get('settings', {})
            if not settings.get('url') or not settings.get('project_key'):
                return False
            
            # Check if API token is available in credentials manager
            api_token = self.credentials_manager.get_credential('jira', 'api_token')
            username = integration.get('credentials', {}).get('username')
            
            return bool(api_token and username)
        
        elif name == 'github':
            # GitHub requires repository and token
            settings = integration.get('settings', {})
            if not settings.get('repository'):
                return False
            
            # Check if token is available in credentials manager
            token = self.credentials_manager.get_credential('github', 'token')
            
            return bool(token)
        
        # Default case for other integrations
        return len(integration.get('credentials', {})) > 0
    
    def get_project_paths(self) -> Dict[str, str]:
        """
        Get all configured project paths.
        
        Returns:
            Dictionary of path configurations by name
        """
        return self.config.get('project', {}).get('paths', {})
    
    def set_project_path(self, path_type: str, path: str) -> None:
        """
        Set a project path.
        
        Args:
            path_type: Path type (e.g., 'source_code', 'documentation')
            path: The path value
        """
        if 'project' not in self.config:
            self.config['project'] = {'paths': {}}
        
        if 'paths' not in self.config['project']:
            self.config['project']['paths'] = {}
        
        self.config['project']['paths'][path_type] = path