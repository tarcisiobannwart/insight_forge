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

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Analyze command (default)
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a project and generate documentation")
    analyze_parser.add_argument(
        "--project",
        type=str,
        required=True,
        help="Path to the project directory to analyze",
    )
    analyze_parser.add_argument(
        "--output-dir",
        type=str,
        help="Directory for generated documentation (default: ./output)",
    )
    analyze_parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
    )
    analyze_parser.add_argument(
        "--profile",
        type=str,
        choices=["default", "minimal", "production"],
        help="Configuration profile to use",
    )
    analyze_parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level",
    )
    
    # Generate config command
    config_parser = subparsers.add_parser("generate-config", help="Generate a default configuration file")
    config_parser.add_argument(
        "output_path",
        type=str,
        help="Path to save the configuration file",
    )
    
    # GitHub export command
    github_parser = subparsers.add_parser("github-export", help="Export documentation to GitHub Pages format")
    github_parser.add_argument(
        "--docs-dir",
        type=str,
        required=True,
        help="Directory containing generated documentation",
    )
    github_parser.add_argument(
        "--output-dir",
        type=str,
        help="Directory to save the GitHub Pages documentation (default: docs-dir/_github_export)",
    )
    github_parser.add_argument(
        "--project-name",
        type=str,
        required=True,
        help="Name of the project",
    )
    github_parser.add_argument(
        "--project-description",
        type=str,
        default="",
        help="Description of the project",
    )
    github_parser.add_argument(
        "--no-jekyll",
        action="store_true",
        help="Disable Jekyll configuration for GitHub Pages",
    )
    
    # GitHub publish command
    github_publish_parser = subparsers.add_parser("github-publish", help="Publish documentation to GitHub Pages")
    github_publish_parser.add_argument(
        "--docs-dir",
        type=str,
        required=True,
        help="Directory containing generated documentation",
    )
    github_publish_parser.add_argument(
        "--repo-url",
        type=str,
        required=True,
        help="GitHub repository URL (https://github.com/user/repo)",
    )
    github_publish_parser.add_argument(
        "--token",
        type=str,
        help="GitHub Personal Access Token (if not provided, will use git credentials)",
    )
    github_publish_parser.add_argument(
        "--username",
        type=str,
        help="GitHub username (if different from local git config)",
    )
    github_publish_parser.add_argument(
        "--branch",
        type=str,
        default="gh-pages",
        help="Branch to publish to (default: gh-pages)",
    )
    github_publish_parser.add_argument(
        "--project-name",
        type=str,
        required=True,
        help="Name of the project",
    )
    github_publish_parser.add_argument(
        "--project-description",
        type=str,
        default="",
        help="Description of the project",
    )
    github_publish_parser.add_argument(
        "--setup-actions",
        action="store_true",
        help="Set up GitHub Actions for automatic documentation generation",
    )
    
    # If no arguments are provided, print help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
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
    if hasattr(args, 'project') and args.project:
        cli_config['project_path'] = args.project
    
    # Add output directory to configuration
    if hasattr(args, 'output_dir') and args.output_dir:
        cli_config['general_output_dir'] = args.output_dir
    
    # Add profile to configuration
    if hasattr(args, 'profile') and args.profile:
        cli_config['general_profile'] = args.profile
    
    # Add log level to configuration
    if hasattr(args, 'log_level') and args.log_level:
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


def handle_analyze_command(args: argparse.Namespace) -> int:
    """Handle the analyze command."""
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


def handle_github_export_command(args: argparse.Namespace) -> int:
    """Handle the github-export command."""
    try:
        # Import GitHub exporter
        from exporters.github_exporter import GitHubExporter
        
        # Validate docs directory
        if not os.path.exists(args.docs_dir):
            console.print(f"[bold red]Error:[/] Documentation directory '{args.docs_dir}' does not exist.")
            return 1
        
        if not os.path.isdir(args.docs_dir):
            console.print(f"[bold red]Error:[/] Documentation path '{args.docs_dir}' is not a directory.")
            return 1
        
        # Determine output directory
        output_dir = args.output_dir if args.output_dir else None
        
        # Initialize exporter
        exporter = GitHubExporter(
            source_dir=args.docs_dir,
            github_repo_dir=None,  # No GitHub repository for export-only
            use_jekyll=not args.no_jekyll
        )
        
        # Export documentation
        console.print("[bold]Exporting documentation to GitHub Pages format...[/]")
        export_path = exporter.export(args.project_name, args.project_description)
        
        console.print(f"[bold green]Documentation exported to:[/] {export_path}")
        return 0
        
    except ImportError:
        console.print("[bold red]Error:[/] GitHub export functionality not available. Make sure all dependencies are installed.")
        return 1
    except Exception as e:
        console.print(f"[bold red]Error during GitHub export:[/] {str(e)}")
        return 1


def handle_github_publish_command(args: argparse.Namespace) -> int:
    """Handle the github-publish command."""
    try:
        # Import GitHub integration modules
        from exporters.github_exporter import GitHubExporter
        from exporters.github_actions import GitHubActionsConfig
        
        # Validate docs directory
        if not os.path.exists(args.docs_dir):
            console.print(f"[bold red]Error:[/] Documentation directory '{args.docs_dir}' does not exist.")
            return 1
        
        if not os.path.isdir(args.docs_dir):
            console.print(f"[bold red]Error:[/] Documentation path '{args.docs_dir}' is not a directory.")
            return 1
        
        # Initialize exporter
        exporter = GitHubExporter(
            source_dir=args.docs_dir,
            github_repo_dir=None,  # We'll handle GitHub interaction separately
            use_jekyll=True
        )
        
        # Export documentation
        console.print("[bold]Preparing documentation for GitHub Pages...[/]")
        export_path = exporter.export(args.project_name, args.project_description)
        
        # Setup GitHub integration
        from exporters.github_integration import GitHubIntegration
        github = GitHubIntegration(
            repo_url=args.repo_url,
            auth_token=args.token,
            username=args.username
        )
        
        # Publish documentation
        console.print("[bold]Publishing documentation to GitHub Pages...[/]")
        result = github.publish_docs(
            docs_dir=export_path,
            branch=args.branch,
            commit_message=f"Update documentation for {args.project_name}"
        )
        
        if not result:
            console.print("[bold red]Error:[/] Failed to publish documentation to GitHub Pages.")
            return 1
        
        # Set up GitHub Actions if requested
        if args.setup_actions:
            console.print("[bold]Setting up GitHub Actions for automatic documentation generation...[/]")
            actions_config = GitHubActionsConfig(
                repo_url=args.repo_url,
                auth_token=args.token,
                username=args.username
            )
            
            result = actions_config.configure_documentation_workflow()
            if not result:
                console.print("[bold yellow]Warning:[/] Failed to set up GitHub Actions workflow.")
            
            # Enable GitHub Pages
            result = actions_config.enable_github_pages(branch=args.branch)
            if not result:
                console.print("[bold yellow]Warning:[/] Failed to enable GitHub Pages. Please enable it manually in repository settings.")
        
        # Parse repository URL to create a GitHub Pages URL
        from urllib.parse import urlparse
        parsed_url = urlparse(args.repo_url)
        if parsed_url.netloc == 'github.com':
            path_parts = parsed_url.path.strip('/').split('/')
            if len(path_parts) >= 2:
                owner = path_parts[0]
                repo = path_parts[1]
                pages_url = f"https://{owner}.github.io/{repo}/"
                console.print(f"[bold green]Documentation published to GitHub Pages:[/] {pages_url}")
        
        console.print("[bold green]Documentation published successfully![/]")
        return 0
        
    except ImportError:
        console.print("[bold red]Error:[/] GitHub publish functionality not available. Make sure all dependencies are installed.")
        return 1
    except Exception as e:
        console.print(f"[bold red]Error during GitHub publish:[/] {str(e)}")
        return 1


def handle_generate_config_command(args: argparse.Namespace) -> int:
    """Handle the generate-config command."""
    return 0 if generate_config_file(args.output_path) else 1


def main() -> int:
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Handle commands
    if args.command == "analyze":
        return handle_analyze_command(args)
    elif args.command == "generate-config":
        return handle_generate_config_command(args)
    elif args.command == "github-export":
        return handle_github_export_command(args)
    elif args.command == "github-publish":
        return handle_github_publish_command(args)
    else:
        console.print("[bold red]Error:[/] Unknown command.")
        return 1


if __name__ == "__main__":
    sys.exit(main())