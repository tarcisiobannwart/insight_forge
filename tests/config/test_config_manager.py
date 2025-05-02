"""
Tests for the configuration manager module.
"""

import os
import tempfile
import pytest
import yaml
import json
from pathlib import Path

# Import the configuration manager
try:
    from insightforge.config.config_manager import ConfigManager, ConfigError
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from insightforge.config.config_manager import ConfigManager, ConfigError


class TestConfigManager:
    """Test suite for the ConfigManager class."""

    def test_default_config(self):
        """Test that the default configuration is loaded correctly."""
        config = ConfigManager()
        assert config.get('general.output_dir') == './output'
        assert config.get('general.log_level') == 'INFO'
        assert config.get('parser.languages.python.enabled') is True

    def test_yaml_config_loading(self):
        """Test loading configuration from a YAML file."""
        with tempfile.NamedTemporaryFile(suffix='.yml', delete=False) as f:
            yaml.dump({
                'general': {
                    'output_dir': './custom-output',
                    'log_level': 'DEBUG'
                }
            }, f)

        config = ConfigManager(config_path=f.name)
        os.unlink(f.name)
        
        assert config.get('general.output_dir') == './custom-output'
        assert config.get('general.log_level') == 'DEBUG'
        # Default values should still be available
        assert config.get('parser.languages.python.enabled') is True

    def test_json_config_loading(self):
        """Test loading configuration from a JSON file."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            json.dump({
                'general': {
                    'output_dir': './json-output',
                    'log_level': 'WARNING'
                }
            }, f)

        config = ConfigManager(config_path=f.name)
        os.unlink(f.name)
        
        assert config.get('general.output_dir') == './json-output'
        assert config.get('general.log_level') == 'WARNING'

    def test_env_var_override(self):
        """Test that environment variables override file configuration."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(suffix='.yml', delete=False) as f:
            yaml.dump({
                'general': {
                    'output_dir': './file-output',
                    'log_level': 'INFO'
                }
            }, f)
        
        # Set environment variables
        os.environ['INSIGHTFORGE_GENERAL_OUTPUT_DIR'] = './env-output'
        
        # Load configuration
        config = ConfigManager(config_path=f.name)
        os.unlink(f.name)
        
        # Environment variable should override file config
        assert config.get('general.output_dir') == './env-output'
        assert config.get('general.log_level') == 'INFO'
        
        # Clean up
        del os.environ['INSIGHTFORGE_GENERAL_OUTPUT_DIR']

    def test_cli_args_override(self):
        """Test that CLI arguments override environment variables and file configuration."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(suffix='.yml', delete=False) as f:
            yaml.dump({
                'general': {
                    'output_dir': './file-output',
                    'log_level': 'INFO'
                }
            }, f)
        
        # Set environment variables
        os.environ['INSIGHTFORGE_GENERAL_OUTPUT_DIR'] = './env-output'
        
        # Set CLI arguments
        cli_args = {
            'general_output_dir': './cli-output'
        }
        
        # Load configuration
        config = ConfigManager(config_path=f.name, cli_args=cli_args)
        os.unlink(f.name)
        
        # CLI arguments should override environment variables and file config
        assert config.get('general.output_dir') == './cli-output'
        
        # Clean up
        del os.environ['INSIGHTFORGE_GENERAL_OUTPUT_DIR']

    def test_config_saving(self):
        """Test saving configuration to a file."""
        config = ConfigManager()
        
        # Modify configuration
        config.set('general.output_dir', './test-output')
        
        # Save configuration to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.yml', delete=False) as f:
            config.save(f.name)
        
        # Load the saved configuration
        new_config = ConfigManager(config_path=f.name)
        os.unlink(f.name)
        
        # Check that the configuration was saved correctly
        assert new_config.get('general.output_dir') == './test-output'

    def test_get_nonexistent_key(self):
        """Test getting a nonexistent configuration key."""
        config = ConfigManager()
        
        # Default value should be returned for nonexistent keys
        assert config.get('nonexistent.key', 'default') == 'default'
        
        # None should be returned if no default is specified
        assert config.get('nonexistent.key') is None

    def test_set_nonexistent_key(self):
        """Test setting a nonexistent configuration key."""
        config = ConfigManager()
        
        # Setting a nonexistent key should create it
        config.set('new.key', 'value')
        assert config.get('new.key') == 'value'
        
        # Setting a nested nonexistent key should create all necessary parent dicts
        config.set('new.nested.key', 'nested-value')
        assert config.get('new.nested.key') == 'nested-value'

    def test_type_conversion(self):
        """Test type conversion of environment variables."""
        # Set environment variables with different types
        os.environ['INSIGHTFORGE_TEST_BOOLEAN'] = 'true'
        os.environ['INSIGHTFORGE_TEST_INTEGER'] = '42'
        os.environ['INSIGHTFORGE_TEST_FLOAT'] = '3.14'
        os.environ['INSIGHTFORGE_TEST_STRING'] = 'hello'
        
        # Load configuration
        config = ConfigManager()
        
        # Check type conversion
        assert config.get('test.boolean') is True
        assert config.get('test.integer') == 42
        assert config.get('test.float') == 3.14
        assert config.get('test.string') == 'hello'
        
        # Clean up
        del os.environ['INSIGHTFORGE_TEST_BOOLEAN']
        del os.environ['INSIGHTFORGE_TEST_INTEGER']
        del os.environ['INSIGHTFORGE_TEST_FLOAT']
        del os.environ['INSIGHTFORGE_TEST_STRING']

    def test_get_profile(self):
        """Test getting the current profile."""
        config = ConfigManager()
        
        # Default profile should be 'default'
        assert config.get_profile() == 'default'
        
        # Setting a different profile
        config.set_profile('production')
        assert config.get_profile() == 'production'
        
        # Profile should be accessible via get() too
        assert config.get('general.profile') == 'production'