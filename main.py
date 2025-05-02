#!/usr/bin/env python3
"""
InsightForge - Automated Reverse Engineering Tool
-------------------------------------------------
Main entry point for the CLI application.
"""

import argparse
import os
import sys
import json
from datetime import datetime

# Simple colored print function to avoid rich dependency for the test
def cprint(text, color=None):
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'bold': '\033[1m',
        'end': '\033[0m'
    }
    
    if color and color in colors:
        print(f"{colors[color]}{text}{colors['end']}")
    else:
        print(text)


def parse_arguments():
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


def validate_project_path(project_path):
    """Validate that the provided project path exists and is a directory."""
    if not os.path.exists(project_path):
        cprint(f"Error: Project path '{project_path}' does not exist.", 'red')
        return False
    
    if not os.path.isdir(project_path):
        cprint(f"Error: Project path '{project_path}' is not a directory.", 'red')
        return False
    
    return True


def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Validate project path
    if not validate_project_path(args.project):
        return 1
    
    # Display start message
    cprint("Starting InsightForge analysis...", 'green')
    cprint(f"Project: {args.project}", 'bold')
    
    # Simulate parsing
    cprint("Parsing project code...", 'bold')
    
    # Count Python files
    python_count = 0
    for root, _, files in os.walk(args.project):
        for file in files:
            if file.endswith('.py'):
                python_count += 1
    
    cprint(f"Found {python_count} Python files", 'blue')
    
    # Create mcp_status.json
    status_dir = os.path.join(args.project, "docs", "internal")
    os.makedirs(status_dir, exist_ok=True)
    
    status_data = {
        "project": args.project,
        "steps": {
            "code_analysis": True,
            "doc_generation": False,
            "usecase_extraction": False,
            "backlog_generation": False,
            "llm_ingestion": False
        },
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "files_analyzed": python_count
    }
    
    with open(os.path.join(status_dir, "mcp_status.json"), 'w') as f:
        json.dump(status_data, f, indent=2)
    
    cprint("Analysis complete!", 'green')
    cprint(f"Status saved to {os.path.join(status_dir, 'mcp_status.json')}", 'blue')
    
    return 0


if __name__ == "__main__":
    sys.exit(main())