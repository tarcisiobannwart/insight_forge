"""
Tests for the configuration schema validation module.
"""

import os
import pytest

# Import the configuration schema validator
try:
    from insightforge.config.config_schema import validate_config, validate_config_paths, validate_full_config
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from insightforge.config.config_schema import validate_config, validate_config_paths, validate_full_config


class TestConfigSchema:
    """Test suite for configuration schema validation."""

    def test_valid_config(self):
        """Test that a valid configuration passes validation."""
        config = {
            'general': {
                'output_dir': './output',
                'log_level': 'INFO'
            },
            'parser': {
                'exclude_dirs': ['venv', 'node_modules'],
                'languages': {
                    'python': {
                        'enabled': True,
                        'extensions': ['.py']
                    }
                }
            },
            'doc_generator': {
                'output_format': 'markdown',
                'generate_diagrams': True
            }
        }
        
        errors = validate_config(config)
        assert len(errors) == 0

    def test_invalid_config_type(self):
        """Test validation fails with invalid types."""
        # Invalid log level
        config = {
            'general': {
                'output_dir': './output',
                'log_level': 'INVALID_LEVEL'  # Not a valid log level
            },
            'parser': {
                'exclude_dirs': ['venv', 'node_modules'],
                'languages': {
                    'python': {
                        'enabled': True,
                        'extensions': ['.py']
                    }
                }
            },
            'doc_generator': {
                'output_format': 'markdown',
                'generate_diagrams': True
            }
        }
        
        # Skip if jsonschema not available
        try:
            from jsonschema import validate
            errors = validate_config(config)
            assert len(errors) > 0
            assert 'log_level' in errors[0]
        except ImportError:
            pass

    def test_invalid_config_missing_required(self):
        """Test validation fails with missing required fields."""
        # Missing required field output_format
        config = {
            'general': {
                'output_dir': './output',
                'log_level': 'INFO'
            },
            'parser': {
                'exclude_dirs': ['venv', 'node_modules'],
                'languages': {
                    'python': {
                        'enabled': True,
                        'extensions': ['.py']
                    }
                }
            },
            'doc_generator': {
                # Missing output_format
                'generate_diagrams': True
            }
        }
        
        # Skip if jsonschema not available
        try:
            from jsonschema import validate
            errors = validate_config(config)
            assert len(errors) > 0
            assert 'output_format' in errors[0]
        except ImportError:
            pass

    def test_path_validation(self):
        """Test validation of paths in configuration."""
        # Valid paths
        config = {
            'general': {
                'output_dir': './output'
            },
            'doc_generator': {
                'template_dir': None  # None is valid
            }
        }
        
        errors = validate_config_paths(config)
        assert len(errors) == 0
        
        # Invalid template directory
        config['doc_generator']['template_dir'] = '/nonexistent/directory'
        errors = validate_config_paths(config)
        assert len(errors) > 0
        assert 'template_dir' in errors[0]

    def test_full_validation(self):
        """Test full configuration validation."""
        # Valid configuration
        config = {
            'general': {
                'output_dir': './output',
                'log_level': 'INFO'
            },
            'parser': {
                'exclude_dirs': ['venv', 'node_modules'],
                'languages': {
                    'python': {
                        'enabled': True,
                        'extensions': ['.py']
                    }
                }
            },
            'doc_generator': {
                'output_format': 'markdown',
                'generate_diagrams': True,
                'template_dir': None
            }
        }
        
        errors = validate_full_config(config)
        assert len(errors) == 0