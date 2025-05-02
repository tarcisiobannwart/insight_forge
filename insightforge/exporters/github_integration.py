"""
GitHub Integration Module
-----------------------
Provides integration with GitHub repositories for documentation publishing.
"""

import os
import subprocess
import logging
import tempfile
import shutil
from typing import Dict, Any, List, Optional, Tuple, Union
import requests
import base64
import json
from urllib.parse import urlparse

class GitHubIntegration:
    """
    Provides integration with GitHub repositories.
    
    This class handles:
    - Authentication with GitHub
    - Publishing documentation to GitHub Pages
    - Creating GitHub Actions workflows
    - Handling GitHub API calls
    """
    
    def __init__(self, 
                 repo_url: str, 
                 auth_token: Optional[str] = None,
                 username: Optional[str] = None):
        """
        Initialize GitHub integration.
        
        Args:
            repo_url: GitHub repository URL (https://github.com/user/repo)
            auth_token: GitHub Personal Access Token for authentication
            username: GitHub username (optional if auth_token is provided)
        """
        self.logger = logging.getLogger(__name__)
        self.repo_url = repo_url
        self.auth_token = auth_token
        self.username = username
        
        # Parse repo details from URL
        self._parse_repo_url()
        
        # Set up API headers
        self.headers = {}
        if auth_token:
            self.headers['Authorization'] = f'token {auth_token}'
    
    def publish_docs(self, 
                    docs_dir: str, 
                    branch: str = "gh-pages",
                    commit_message: str = "Update documentation",
                    method: str = "git") -> bool:
        """
        Publish documentation to GitHub Pages.
        
        Args:
            docs_dir: Directory containing documentation to publish
            branch: Branch to publish to (usually gh-pages for GitHub Pages)
            commit_message: Commit message
            method: Publication method ('git' or 'api')
            
        Returns:
            True if successful, False otherwise
        """
        if method == 'git':
            return self._publish_with_git(docs_dir, branch, commit_message)
        elif method == 'api':
            return self._publish_with_api(docs_dir, branch, commit_message)
        else:
            self.logger.error(f"Unknown publication method: {method}")
            return False
    
    def setup_github_actions(self, 
                           workflow_name: str = "documentation", 
                           on_push_branches: List[str] = ["main"],
                           on_schedule: Optional[str] = "0 0 * * 0") -> bool:
        """
        Set up GitHub Actions workflow for automatic documentation generation.
        
        Args:
            workflow_name: Name for the workflow file
            on_push_branches: Branches to trigger workflow on push
            on_schedule: Cron schedule expression (default: every Sunday at midnight)
            
        Returns:
            True if successful, False otherwise
        """
        # Workflow content
        workflow = {
            "name": "Generate Documentation",
            "on": {
                "push": {
                    "branches": on_push_branches
                }
            },
            "jobs": {
                "build-docs": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout repository",
                            "uses": "actions/checkout@v2"
                        },
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v2",
                            "with": {
                                "python-version": "3.9"
                            }
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -e ."
                        },
                        {
                            "name": "Generate documentation",
                            "run": "python -m insightforge.main generate-docs --output ./docs"
                        },
                        {
                            "name": "GitHub Pages deployment",
                            "uses": "JamesIves/github-pages-deploy-action@v4",
                            "with": {
                                "branch": "gh-pages",
                                "folder": "docs",
                                "clean": "true"
                            }
                        }
                    ]
                }
            }
        }
        
        # Add schedule if provided
        if on_schedule:
            workflow["on"]["schedule"] = [{"cron": on_schedule}]
        
        # Convert to YAML
        import yaml
        workflow_yaml = yaml.dump(workflow, sort_keys=False)
        
        # Determine if we're using git CLI or API
        if self.auth_token:
            return self._create_workflow_file_api(workflow_name, workflow_yaml)
        else:
            return self._create_workflow_file_git(workflow_name, workflow_yaml)
    
    def enable_github_pages(self, branch: str = "gh-pages", path: str = "/") -> bool:
        """
        Enable GitHub Pages for the repository.
        
        Args:
            branch: Branch to use for GitHub Pages
            path: Path within the branch (/ or /docs)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.auth_token:
            self.logger.error("GitHub token required to enable GitHub Pages")
            return False
        
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pages"
        data = {
            "source": {
                "branch": branch,
                "path": path.lstrip('/')
            }
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code in (201, 204):
                self.logger.info(f"GitHub Pages enabled for {self.repo_url}")
                return True
            else:
                self.logger.error(f"Failed to enable GitHub Pages: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Error enabling GitHub Pages: {str(e)}")
            return False
    
    def _parse_repo_url(self) -> None:
        """Parse repository URL to extract owner and repo name."""
        parsed_url = urlparse(self.repo_url)
        
        # Handle different URL formats
        if parsed_url.netloc == 'github.com':
            # https://github.com/user/repo
            path_parts = parsed_url.path.strip('/').split('/')
            if len(path_parts) >= 2:
                self.owner = path_parts[0]
                self.repo = path_parts[1]
            else:
                raise ValueError(f"Invalid GitHub URL: {self.repo_url}")
        else:
            # git@github.com:user/repo.git
            if '@' in self.repo_url and ':' in self.repo_url:
                path = self.repo_url.split(':')[-1]
                path = path.replace('.git', '')
                path_parts = path.split('/')
                if len(path_parts) >= 2:
                    self.owner = path_parts[0]
                    self.repo = path_parts[1]
                else:
                    raise ValueError(f"Invalid GitHub URL: {self.repo_url}")
            else:
                raise ValueError(f"Invalid GitHub URL: {self.repo_url}")
    
    def _publish_with_git(self, 
                         docs_dir: str, 
                         branch: str = "gh-pages",
                         commit_message: str = "Update documentation") -> bool:
        """Publish documentation using Git CLI."""
        try:
            # Create a temporary directory for the operation
            temp_dir = tempfile.mkdtemp()
            
            try:
                # Clone the repository to the temporary directory
                self.logger.info(f"Cloning repository {self.repo_url} to {temp_dir}")
                
                # Use authentication if available
                if self.auth_token:
                    # Create URL with authentication
                    auth_url = f"https://{self.auth_token}@github.com/{self.owner}/{self.repo}.git"
                    subprocess.check_call(['git', 'clone', auth_url, temp_dir], stderr=subprocess.PIPE)
                else:
                    subprocess.check_call(['git', 'clone', self.repo_url, temp_dir], stderr=subprocess.PIPE)
                
                # Configure Git user if needed
                if self.username:
                    subprocess.check_call(['git', 'config', 'user.name', self.username], cwd=temp_dir)
                    subprocess.check_call(['git', 'config', 'user.email', f"{self.username}@users.noreply.github.com"], cwd=temp_dir)
                
                # Check if branch exists
                branches = subprocess.check_output(['git', 'branch', '-a'], cwd=temp_dir, universal_newlines=True)
                branch_exists = f"remotes/origin/{branch}" in branches
                
                # Create or checkout the branch
                if branch_exists:
                    subprocess.check_call(['git', 'checkout', branch], cwd=temp_dir)
                else:
                    # Create an orphan branch
                    subprocess.check_call(['git', 'checkout', '--orphan', branch], cwd=temp_dir)
                    # Remove all files
                    subprocess.check_call(['git', 'rm', '-rf', '.'], cwd=temp_dir, stderr=subprocess.PIPE)
                
                # Copy documentation files
                for item in os.listdir(docs_dir):
                    source_path = os.path.join(docs_dir, item)
                    target_path = os.path.join(temp_dir, item)
                    
                    if os.path.isfile(source_path):
                        shutil.copy2(source_path, target_path)
                    elif os.path.isdir(source_path):
                        if os.path.exists(target_path):
                            shutil.rmtree(target_path)
                        shutil.copytree(source_path, target_path)
                
                # Commit and push changes
                subprocess.check_call(['git', 'add', '.'], cwd=temp_dir)
                
                # Check if there are changes to commit
                status = subprocess.check_output(['git', 'status', '--porcelain'], cwd=temp_dir, universal_newlines=True)
                if status.strip():
                    subprocess.check_call(['git', 'commit', '-m', commit_message], cwd=temp_dir)
                    subprocess.check_call(['git', 'push', 'origin', branch], cwd=temp_dir)
                    self.logger.info(f"Documentation published to {self.repo_url} ({branch} branch)")
                else:
                    self.logger.info("No changes to commit")
                
                return True
                
            finally:
                # Clean up temporary directory
                shutil.rmtree(temp_dir)
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git operation failed: {e.stderr.decode() if e.stderr else str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error publishing documentation: {str(e)}")
            return False
    
    def _publish_with_api(self, 
                         docs_dir: str, 
                         branch: str = "gh-pages",
                         commit_message: str = "Update documentation") -> bool:
        """Publish documentation using GitHub API."""
        if not self.auth_token:
            self.logger.error("GitHub token required for API publishing")
            return False
        
        try:
            # Get the current commit SHA of the branch if it exists
            sha = self._get_branch_sha(branch)
            
            # If branch doesn't exist, get the default branch SHA
            if not sha:
                default_sha = self._get_default_branch_sha()
                if not default_sha:
                    self.logger.error("Could not determine base SHA for commit")
                    return False
                
                # Create the branch
                created = self._create_branch(branch, default_sha)
                if not created:
                    self.logger.error(f"Failed to create branch: {branch}")
                    return False
                
                # Get the new branch SHA
                sha = self._get_branch_sha(branch)
                if not sha:
                    self.logger.error(f"Could not get SHA for new branch: {branch}")
                    return False
            
            # Upload files
            tree_sha = self._create_tree(docs_dir, sha)
            if not tree_sha:
                self.logger.error("Failed to create tree for files")
                return False
            
            # Create a commit
            commit_sha = self._create_commit(tree_sha, sha, commit_message)
            if not commit_sha:
                self.logger.error("Failed to create commit")
                return False
            
            # Update the branch reference
            updated = self._update_reference(branch, commit_sha)
            if not updated:
                self.logger.error(f"Failed to update branch reference: {branch}")
                return False
            
            self.logger.info(f"Documentation published to {self.repo_url} ({branch} branch)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error publishing documentation: {str(e)}")
            return False
    
    def _get_branch_sha(self, branch: str) -> Optional[str]:
        """Get the SHA of the latest commit on a branch."""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs/heads/{branch}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()['object']['sha']
            elif response.status_code == 404:
                # Branch doesn't exist
                return None
            else:
                self.logger.error(f"Failed to get branch SHA: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting branch SHA: {str(e)}")
            return None
    
    def _get_default_branch_sha(self) -> Optional[str]:
        """Get the SHA of the latest commit on the default branch."""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                default_branch = response.json()['default_branch']
                return self._get_branch_sha(default_branch)
            else:
                self.logger.error(f"Failed to get repository info: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting default branch: {str(e)}")
            return None
    
    def _create_branch(self, branch: str, sha: str) -> bool:
        """Create a new branch pointing to a specific commit SHA."""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs"
        data = {
            "ref": f"refs/heads/{branch}",
            "sha": sha
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code == 201:
                return True
            else:
                self.logger.error(f"Failed to create branch: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Error creating branch: {str(e)}")
            return False
    
    def _create_tree(self, docs_dir: str, base_sha: str) -> Optional[str]:
        """Create a new git tree with all files from docs_dir."""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees"
        
        tree = []
        for root, dirs, files in os.walk(docs_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, docs_dir)
                
                # Skip .git files
                if '.git' in rel_path:
                    continue
                
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Convert path separators to forward slashes
                rel_path = rel_path.replace('\\', '/')
                
                # Encode content as base64
                encoded_content = base64.b64encode(content).decode('utf-8')
                
                tree.append({
                    "path": rel_path,
                    "mode": "100644",  # File mode (100644 for file)
                    "type": "blob",
                    "content": encoded_content
                })
        
        data = {
            "base_tree": base_sha,
            "tree": tree
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code == 201:
                return response.json()['sha']
            else:
                self.logger.error(f"Failed to create tree: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error creating tree: {str(e)}")
            return None
    
    def _create_commit(self, tree_sha: str, parent_sha: str, message: str) -> Optional[str]:
        """Create a new commit with the given tree and parent."""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/commits"
        data = {
            "message": message,
            "tree": tree_sha,
            "parents": [parent_sha]
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code == 201:
                return response.json()['sha']
            else:
                self.logger.error(f"Failed to create commit: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error creating commit: {str(e)}")
            return None
    
    def _update_reference(self, branch: str, sha: str) -> bool:
        """Update a branch reference to point to a new commit."""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs/heads/{branch}"
        data = {
            "sha": sha,
            "force": True
        }
        
        try:
            response = requests.patch(url, headers=self.headers, json=data)
            if response.status_code == 200:
                return True
            else:
                self.logger.error(f"Failed to update reference: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Error updating reference: {str(e)}")
            return False
    
    def _create_workflow_file_git(self, workflow_name: str, content: str) -> bool:
        """Create a GitHub Actions workflow file using Git."""
        try:
            # Create a temporary directory for the operation
            temp_dir = tempfile.mkdtemp()
            
            try:
                # Clone the repository to the temporary directory
                self.logger.info(f"Cloning repository {self.repo_url} to {temp_dir}")
                
                # Use authentication if available
                if self.auth_token:
                    # Create URL with authentication
                    auth_url = f"https://{self.auth_token}@github.com/{self.owner}/{self.repo}.git"
                    subprocess.check_call(['git', 'clone', auth_url, temp_dir], stderr=subprocess.PIPE)
                else:
                    subprocess.check_call(['git', 'clone', self.repo_url, temp_dir], stderr=subprocess.PIPE)
                
                # Configure Git user if needed
                if self.username:
                    subprocess.check_call(['git', 'config', 'user.name', self.username], cwd=temp_dir)
                    subprocess.check_call(['git', 'config', 'user.email', f"{self.username}@users.noreply.github.com"], cwd=temp_dir)
                
                # Create workflow directory if it doesn't exist
                workflows_dir = os.path.join(temp_dir, '.github', 'workflows')
                os.makedirs(workflows_dir, exist_ok=True)
                
                # Write workflow file
                workflow_file = os.path.join(workflows_dir, f"{workflow_name}.yml")
                with open(workflow_file, 'w') as f:
                    f.write(content)
                
                # Commit and push changes
                subprocess.check_call(['git', 'add', workflow_file], cwd=temp_dir)
                
                # Check if there are changes to commit
                status = subprocess.check_output(['git', 'status', '--porcelain'], cwd=temp_dir, universal_newlines=True)
                if status.strip():
                    subprocess.check_call(['git', 'commit', '-m', f"Add GitHub Actions workflow for documentation"], cwd=temp_dir)
                    subprocess.check_call(['git', 'push', 'origin', 'HEAD'], cwd=temp_dir)
                    self.logger.info(f"GitHub Actions workflow created in {self.repo_url}")
                else:
                    self.logger.info("No changes to commit (workflow file already exists)")
                
                return True
                
            finally:
                # Clean up temporary directory
                shutil.rmtree(temp_dir)
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git operation failed: {e.stderr.decode() if e.stderr else str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error creating workflow file: {str(e)}")
            return False
    
    def _create_workflow_file_api(self, workflow_name: str, content: str) -> bool:
        """Create a GitHub Actions workflow file using GitHub API."""
        if not self.auth_token:
            self.logger.error("GitHub token required for API operation")
            return False
        
        workflow_path = f".github/workflows/{workflow_name}.yml"
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{workflow_path}"
        
        # Encode content as base64
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        data = {
            "message": "Add GitHub Actions workflow for documentation",
            "content": encoded_content
        }
        
        # Check if file already exists
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                # File exists, get its SHA for update
                sha = response.json()['sha']
                data['sha'] = sha
        except Exception:
            # File doesn't exist, continue with creation
            pass
        
        try:
            response = requests.put(url, headers=self.headers, json=data)
            if response.status_code in (200, 201):
                self.logger.info(f"GitHub Actions workflow created/updated in {self.repo_url}")
                return True
            else:
                self.logger.error(f"Failed to create workflow file: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Error creating workflow file: {str(e)}")
            return False