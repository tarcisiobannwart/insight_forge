"""
Utility functions for reverse engineering.
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime


def save_json(data: Dict[str, Any], file_path: str) -> None:
    """Save data to a JSON file."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def load_json(file_path: str) -> Dict[str, Any]:
    """Load data from a JSON file."""
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_mcp_status(
    project_path: str,
    steps: Dict[str, bool] = None,
    output_path: str = None
) -> str:
    """Create or update the MCP status file."""
    if steps is None:
        steps = {
            "code_analysis": False,
            "doc_generation": False,
            "usecase_extraction": False,
            "backlog_generation": False,
            "llm_ingestion": False
        }
    
    # Create status data
    status_data = {
        "project": project_path,
        "steps": steps,
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }
    
    # Determine output path
    if output_path is None:
        # Default to project's docs/internal directory
        output_path = os.path.join(project_path, "docs", "internal", "mcp_status.json")
    
    # Save the status file
    save_json(status_data, output_path)
    
    return output_path


def update_mcp_status(
    project_path: str,
    step: str,
    status: bool,
    status_path: Optional[str] = None
) -> None:
    """Update a specific step in the MCP status file."""
    # Determine status file path
    if status_path is None:
        status_path = os.path.join(project_path, "docs", "internal", "mcp_status.json")
    
    # Load existing status
    status_data = load_json(status_path) if os.path.exists(status_path) else {
        "project": project_path,
        "steps": {},
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }
    
    # Update the step
    if "steps" not in status_data:
        status_data["steps"] = {}
    
    status_data["steps"][step] = status
    status_data["generated_at"] = datetime.utcnow().isoformat() + "Z"
    
    # Save the updated status
    save_json(status_data, status_path)