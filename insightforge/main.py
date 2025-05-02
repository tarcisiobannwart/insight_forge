#!/usr/bin/env python3
"""
InsightForge - Automated Reverse Engineering Tool
-------------------------------------------------
Main entry point for the CLI application.
"""

import argparse
import os
import sys
import logging
from typing import Optional, Dict, Any

from rich.console import Console
from rich.logging import RichHandler

# Local imports
try:
    from reverse_engineering import code_parser
    from config import ConfigManager, load_config
    from config.config_schema import validate_full_config
except ImportError:
    # Add project root to path if running from project root
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from insightforge.reverse_engineering import code_parser
    from insightforge.config import ConfigManager, load_config
    from insightforge.config.config_schema import validate_full_config


# Set up console for rich output
console = Console()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger("insightforge")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="InsightForge - Automated Reverse Engineering Tool"
    )
    parser.add_argument(
        "--project",
        type=str,
        required=True,
        help="Path to the project directory to analyze",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Directory for generated documentation (default: ./output)",
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
    )
    parser.add_argument(
        "--profile",
        type=str,
        choices=["default", "minimal", "production"],
        help="Configuration profile to use",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level",
    )
    parser.add_argument(
        "--generate-config",
        type=str,
        help="Generate a default configuration file at the specified path and exit",
    )
    return parser.parse_args()


def validate_project_path(project_path: str) -> bool:
    """Validate that the provided project path exists and is a directory."""
    if not os.path.exists(project_path):
        console.print(f"[bold red]Error:[/] Project path '{project_path}' does not exist.")
        return False
    
    if not os.path.isdir(project_path):
        console.print(f"[bold red]Error:[/] Project path '{project_path}' is not a directory.")
        return False
    
    return True


def prepare_cli_config(args: argparse.Namespace) -> Dict[str, Any]:
    """Prepare configuration from command-line arguments."""
    cli_config = {}
    
    # Add project path to configuration
    if args.project:
        cli_config['project_path'] = args.project
    
    # Add output directory to configuration
    if args.output_dir:
        cli_config['general_output_dir'] = args.output_dir
    
    # Add profile to configuration
    if args.profile:
        cli_config['general_profile'] = args.profile
    
    # Add log level to configuration
    if args.log_level:
        cli_config['general_log_level'] = args.log_level
    
    return cli_config


def setup_logging(log_level: str) -> None:
    """Set up logging with the specified level."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    
    # Configure root logger
    logging.getLogger().setLevel(numeric_level)
    
    # Configure rich handler
    for handler in logging.getLogger().handlers:
        if isinstance(handler, RichHandler):
            handler.setLevel(numeric_level)


def generate_config_file(file_path: str) -> bool:
    """
    Generate a default configuration file.
    
    Args:
        file_path: Path to save the configuration file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create configuration manager with default settings
        config = ConfigManager()
        
        # Save configuration to the specified path
        config.save(file_path)
        
        console.print(f"[bold green]Default configuration generated at:[/] {file_path}")
        return True
        
    except Exception as e:
        console.print(f"[bold red]Error generating configuration file:[/] {str(e)}")
        return False


def main() -> int:
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Check if we should generate a config file and exit
    if args.generate_config:
        return 0 if generate_config_file(args.generate_config) else 1
    
    # Validate project path
    if not validate_project_path(args.project):
        return 1
    
    # Prepare CLI configuration
    cli_config = prepare_cli_config(args)
    
    # Load configuration
    try:
        config = load_config(args.config, cli_args=cli_config)
        
        # Validate configuration
        errors = validate_full_config(config.as_dict())
        if errors:
            console.print("[bold red]Configuration errors:[/]")
            for error in errors:
                console.print(f"  - {error}")
            return 1
        
        # Set up logging based on configuration
        log_level = config.get('general.log_level', 'INFO')
        setup_logging(log_level)
        
    except Exception as e:
        console.print(f"[bold red]Error loading configuration:[/] {str(e)}")
        return 1
    
    # Display start message
    console.print("[bold green]Starting InsightForge analysis...[/]")
    console.print(f"Project: [bold]{args.project}[/]")
    console.print(f"Output directory: [bold]{config.get('general.output_dir', './output')}[/]")
    console.print(f"Profile: [bold]{config.get('general.profile', 'default')}[/]")
    
    # Create output directory if it doesn't exist
    output_dir = config.get('general.output_dir')
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize components based on configuration
    parser_config = config.get('parser', {})
    
    # Initialize the code parser
    parser = code_parser.CodeParser(
        project_path=args.project,
        exclude_dirs=parser_config.get('exclude_dirs', []),
        exclude_files=parser_config.get('exclude_files', [])
    )
    
    # Parse the code
    console.print("[bold]Parsing project code...[/]")
    result = parser.parse()
    
    # TODO: Add more components as they are implemented
    
    console.print("[bold green]Analysis complete![/]")
    return 0


if __name__ == "__main__":
    sys.exit(main())