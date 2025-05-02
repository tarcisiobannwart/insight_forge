#!/usr/bin/env python3
"""
InsightForge - Automated Reverse Engineering Tool
-------------------------------------------------
Main entry point for the CLI application.
"""

import argparse
import os
import sys
from typing import Optional

from rich.console import Console

# Local imports
try:
    from reverse_engineering import code_parser
except ImportError:
    # Add project root to path if running from project root
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from insightforge.reverse_engineering import code_parser


console = Console()


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


def main() -> int:
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Validate project path
    if not validate_project_path(args.project):
        return 1
    
    # Display start message
    console.print("[bold green]Starting InsightForge analysis...[/]")
    console.print(f"Project: [bold]{args.project}[/]")
    
    # Initialize the code parser
    parser = code_parser.CodeParser(args.project)
    
    # Parse the code
    console.print("[bold]Parsing project code...[/]")
    result = parser.parse()
    
    # TODO: Add more components as they are implemented
    
    console.print("[bold green]Analysis complete![/]")
    return 0


if __name__ == "__main__":
    sys.exit(main())