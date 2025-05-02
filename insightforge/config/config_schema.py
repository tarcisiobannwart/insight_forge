"""
Configuration Schema Module
------------------------
Defines the schema for validating InsightForge configuration.
"""

import os
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

try:
    from jsonschema import validate, ValidationError, Draft7Validator
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    logger.warning("jsonschema not installed. Configuration validation disabled.")
    JSONSCHEMA_AVAILABLE = False


# Configuration schema definition
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "general": {
            "type": "object",
            "properties": {
                "output_dir": {"type": "string"},
                "log_level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
                "profile": {"type": "string"}
            },
            "required": ["output_dir", "log_level"],
            "additionalProperties": False
        },
        "parser": {
            "type": "object",
            "properties": {
                "exclude_dirs": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "exclude_files": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "languages": {
                    "type": "object",
                    "properties": {
                        "python": {
                            "type": "object",
                            "properties": {
                                "enabled": {"type": "boolean"},
                                "extensions": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "detect_docstrings": {"type": "boolean"},
                                "detect_types": {"type": "boolean"}
                            },
                            "required": ["enabled", "extensions"]
                        },
                        "php": {
                            "type": "object",
                            "properties": {
                                "enabled": {"type": "boolean"},
                                "extensions": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "detect_docstrings": {"type": "boolean"}
                            },
                            "required": ["enabled", "extensions"]
                        },
                        "javascript": {
                            "type": "object",
                            "properties": {
                                "enabled": {"type": "boolean"},
                                "extensions": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "detect_jsdoc": {"type": "boolean"}
                            },
                            "required": ["enabled", "extensions"]
                        },
                        "typescript": {
                            "type": "object",
                            "properties": {
                                "enabled": {"type": "boolean"},
                                "extensions": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "detect_tsdoc": {"type": "boolean"}
                            },
                            "required": ["enabled", "extensions"]
                        }
                    }
                }
            }
        },
        "doc_generator": {
            "type": "object",
            "properties": {
                "output_format": {
                    "type": "string",
                    "enum": ["markdown", "html", "pdf"]
                },
                "template_dir": {
                    "type": ["string", "null"]
                },
                "generate_diagrams": {"type": "boolean"},
                "diagram_format": {
                    "type": "string",
                    "enum": ["mermaid", "plantuml"]
                },
                "diagram_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["class", "module", "sequence", "component", "state"]
                    }
                },
                "index_template": {"type": "string"},
                "include_source_links": {"type": "boolean"}
            },
            "required": ["output_format", "generate_diagrams"]
        },
        "business_rules": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "extract_from_code": {"type": "boolean"},
                "extract_from_comments": {"type": "boolean"},
                "extract_from_docstrings": {"type": "boolean"},
                "patterns": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["enabled"]
        },
        "usecase_extractor": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "extract_from_docstrings": {"type": "boolean"},
                "extract_from_comments": {"type": "boolean"},
                "extract_from_method_names": {"type": "boolean"}
            },
            "required": ["enabled"]
        },
        "backlog_builder": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "format": {
                    "type": "string",
                    "enum": ["markdown", "json", "yaml", "csv"]
                },
                "include_priority": {"type": "boolean"},
                "include_story_points": {"type": "boolean"}
            },
            "required": ["enabled", "format"]
        },
        "llm": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "provider": {
                    "type": "string",
                    "enum": ["ollama", "openai", "anthropic", "local", "huggingface"]
                },
                "model": {"type": "string"},
                "endpoint": {"type": "string"},
                "max_tokens": {"type": "integer"},
                "temperature": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                },
                "embeddings_model": {"type": "string"}
            },
            "required": ["enabled"]
        }
    },
    "required": ["general", "parser", "doc_generator"]
}


def validate_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate configuration against the schema.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of validation error messages, empty if valid
    """
    if not JSONSCHEMA_AVAILABLE:
        logger.warning("jsonschema not installed. Skipping configuration validation.")
        return []
    
    try:
        validate(instance=config, schema=CONFIG_SCHEMA)
        return []
    except ValidationError as e:
        # Get the error message for the validation error
        return [f"Configuration error at {'.'.join(str(p) for p in e.path)}: {e.message}"]
    
    
def validate_config_paths(config: Dict[str, Any]) -> List[str]:
    """
    Validate that paths in the configuration exist.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of validation error messages, empty if valid
    """
    errors = []
    
    # Check template directory if specified
    template_dir = config.get('doc_generator', {}).get('template_dir')
    if template_dir and template_dir != "default" and not os.path.isdir(template_dir):
        errors.append(f"Template directory does not exist: {template_dir}")
    
    # Check output directory
    output_dir = config.get('general', {}).get('output_dir')
    if output_dir:
        # Output directory will be created, no need to check if it exists
        pass
    
    return errors


def validate_full_config(config: Dict[str, Any]) -> List[str]:
    """
    Perform full configuration validation.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of validation error messages, empty if valid
    """
    errors = validate_config(config)
    errors.extend(validate_config_paths(config))
    return errors