"""
GitHub Actions Configuration
-------------------------
Sets up GitHub Actions for automatic documentation generation.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
from jinja2 import Environment, FileSystemLoader

from .github_integration import GitHubIntegration

class GitHubActionsConfig:
    """
    Configures GitHub Actions for automatic documentation generation.
    
    This class handles:
    - Creating GitHub Actions workflow files
    - Configuring workflow triggers and settings
    - Setting up documentation generation and publication
    """
    
    def __init__(self, 
                 repo_url: str,
                 auth_token: Optional[str] = None,
                 username: Optional[str] = None):
        """
        Initialize GitHub Actions configuration.
        
        Args:
            repo_url: GitHub repository URL
            auth_token: GitHub Personal Access Token
            username: GitHub username
        """
        self.logger = logging.getLogger(__name__)
        self.github = GitHubIntegration(repo_url, auth_token, username)
        
        # Get templates directory
        self.templates_dir = os.path.join(os.path.dirname(__file__), 'templates', 'github_actions')
        
        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def configure_documentation_workflow(self, 
                                      workflow_name: str = "documentation",
                                      branches: List[str] = ["main"],
                                      schedule: Optional[str] = "0 0 * * 0",
                                      python_version: str = "3.9",
                                      output_folder: str = "docs",
                                      deploy_branch: str = "gh-pages") -> bool:
        """
        Configure GitHub Actions workflow for documentation generation.
        
        Args:
            workflow_name: Name for the workflow file
            branches: Branches to trigger workflow on push
            schedule: Cron schedule expression (default: every Sunday at midnight)
            python_version: Python version to use
            output_folder: Folder to deploy to GitHub Pages
            deploy_branch: Branch to deploy to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load template
            template = self.env.get_template('documentation.yml.j2')
            
            # Render template
            workflow_content = template.render(
                branches=branches,
                schedule=schedule,
                python_version=python_version,
                output_folder=output_folder,
                deploy_branch=deploy_branch
            )
            
            # Create workflow file
            return self.github.setup_github_actions(workflow_name, branches, schedule)
            
        except Exception as e:
            self.logger.error(f"Error configuring documentation workflow: {str(e)}")
            return False
    
    def enable_github_pages(self, branch: str = "gh-pages", path: str = "/") -> bool:
        """
        Enable GitHub Pages for the repository.
        
        Args:
            branch: Branch to use for GitHub Pages
            path: Path within the branch (/ or /docs)
            
        Returns:
            True if successful, False otherwise
        """
        return self.github.enable_github_pages(branch, path)