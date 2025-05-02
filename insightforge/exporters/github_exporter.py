"""
GitHub Documentation Exporter
----------------------------
Exports documentation to GitHub-compatible formats and structures.
"""

import os
import re
import shutil
import logging
import subprocess
from typing import Dict, Any, List, Optional, Union
import json
import yaml

class GitHubExporter:
    """
    Exports documentation for GitHub repositories, with support for GitHub Pages.
    
    This class handles:
    - Copying and formatting documentation for GitHub display
    - Creating GitHub Pages configuration
    - Setting up navigation and site structure
    - Optional publication to GitHub repository
    """
    
    def __init__(self, source_dir: str, 
                 github_repo_dir: Optional[str] = None,
                 github_pages_dir: str = "docs",
                 use_jekyll: bool = True):
        """
        Initialize the GitHub exporter.
        
        Args:
            source_dir: Directory containing generated documentation
            github_repo_dir: Path to GitHub repository (None for only preparing files)
            github_pages_dir: Directory in repository for GitHub Pages (usually "docs")
            use_jekyll: Whether to configure for GitHub Pages with Jekyll
        """
        self.source_dir = source_dir
        self.github_repo_dir = github_repo_dir
        self.github_pages_dir = github_pages_dir
        self.use_jekyll = use_jekyll
        self.logger = logging.getLogger(__name__)
        
        # Get full path to GitHub Pages directory
        if github_repo_dir:
            self.target_dir = os.path.join(github_repo_dir, github_pages_dir)
        else:
            # If no repo directory specified, create a standalone export
            self.target_dir = os.path.join(source_dir, "_github_export")
    
    def export(self, project_name: str, project_description: str = "") -> str:
        """
        Export documentation to GitHub format.
        
        Args:
            project_name: Name of the project
            project_description: Description of the project
            
        Returns:
            Path to the exported documentation
        """
        self.logger.info(f"Exporting documentation to GitHub format for {project_name}")
        
        # Create target directory
        os.makedirs(self.target_dir, exist_ok=True)
        
        # Copy documentation with GitHub-specific adjustments
        self._copy_documentation()
        
        # Set up GitHub Pages if needed
        if self.use_jekyll:
            self._setup_jekyll(project_name, project_description)
            
            # Create index.html for GitHub Pages
            self._create_docs_index()
        
        # Fix internal links
        self._fix_links()
        
        return self.target_dir
    
    def publish(self, branch: str = "gh-pages", 
                commit_message: str = "Update documentation",
                force_push: bool = False) -> bool:
        """
        Publish documentation to the GitHub repository.
        
        Args:
            branch: Branch to publish to (usually gh-pages for GitHub Pages)
            commit_message: Commit message
            force_push: Whether to force push (use with caution)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.github_repo_dir:
            self.logger.error("GitHub repository directory not specified")
            return False
        
        try:
            # Change to repository directory
            original_dir = os.getcwd()
            os.chdir(self.github_repo_dir)
            
            # Check if we're in a git repository
            if not os.path.exists('.git'):
                self.logger.error(f"{self.github_repo_dir} is not a git repository")
                return False
            
            # Determine current branch
            current_branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                universal_newlines=True
            ).strip()
            
            # See if branch already exists
            branches = subprocess.check_output(
                ['git', 'branch'],
                universal_newlines=True
            )
            
            branch_exists = branch in [b.strip().replace('* ', '') for b in branches.split('\n') if b]
            
            if branch == current_branch:
                # Already on the right branch, just add files
                subprocess.check_call(['git', 'add', self.github_pages_dir])
                subprocess.check_call(['git', 'commit', '-m', commit_message])
            elif branch_exists:
                # Branch exists, need to checkout and update
                subprocess.check_call(['git', 'checkout', branch])
                subprocess.check_call(['git', 'add', self.github_pages_dir])
                subprocess.check_call(['git', 'commit', '-m', commit_message])
                subprocess.check_call(['git', 'checkout', current_branch])
            else:
                # Create orphan branch for GitHub Pages
                subprocess.check_call(['git', 'checkout', '--orphan', branch])
                # Remove everything except the documentation
                subprocess.check_call(['git', 'rm', '-rf', '.'])
                # Now add the docs directory
                subprocess.check_call(['git', 'add', self.github_pages_dir])
                subprocess.check_call(['git', 'commit', '-m', commit_message])
                # Return to original branch
                subprocess.check_call(['git', 'checkout', current_branch])
            
            # Push to remote
            push_command = ['git', 'push', 'origin', branch]
            if force_push:
                push_command.insert(2, '-f')
            
            subprocess.check_call(push_command)
            self.logger.info(f"Documentation published to branch {branch}")
            
            # Return to original directory
            os.chdir(original_dir)
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git operation failed: {str(e)}")
            # Return to original directory on error
            if 'original_dir' in locals():
                os.chdir(original_dir)
            return False
        except Exception as e:
            self.logger.error(f"Publication failed: {str(e)}")
            # Return to original directory on error
            if 'original_dir' in locals():
                os.chdir(original_dir)
            return False
    
    def _copy_documentation(self) -> None:
        """Copy and adjust documentation files to target directory."""
        # Remove existing files in target directory if it exists
        if os.path.exists(self.target_dir):
            for item in os.listdir(self.target_dir):
                item_path = os.path.join(self.target_dir, item)
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path) and item not in ['.git']:
                    shutil.rmtree(item_path)
        
        # Create target directory if it doesn't exist
        os.makedirs(self.target_dir, exist_ok=True)
        
        # Copy documentation files
        for item in os.listdir(self.source_dir):
            source_path = os.path.join(self.source_dir, item)
            target_path = os.path.join(self.target_dir, item)
            
            # Skip _github_export directory if it exists
            if item == '_github_export':
                continue
                
            if os.path.isfile(source_path):
                shutil.copy2(source_path, target_path)
            elif os.path.isdir(source_path):
                shutil.copytree(source_path, target_path, dirs_exist_ok=True)
    
    def _setup_jekyll(self, project_name: str, project_description: str) -> None:
        """Set up Jekyll configuration for GitHub Pages."""
        import datetime
        from jinja2 import Environment, FileSystemLoader
        
        # Get templates directory
        templates_dir = os.path.join(os.path.dirname(__file__), 'templates', 'github')
        
        # Setup Jinja2 environment
        env = Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Create layouts directory
        layouts_dir = os.path.join(self.target_dir, '_layouts')
        os.makedirs(layouts_dir, exist_ok=True)
        
        # Determine what documentation sections are available
        has_modules = os.path.exists(os.path.join(self.source_dir, 'modules'))
        has_diagrams = os.path.exists(os.path.join(self.source_dir, 'diagrams'))
        has_business_rules = os.path.exists(os.path.join(self.source_dir, 'business_rules'))
        
        # Get counts
        classes_count = len([f for f in os.listdir(os.path.join(self.source_dir, 'classes')) 
                           if f.endswith('.md')]) if os.path.exists(os.path.join(self.source_dir, 'classes')) else 0
        
        functions_count = len([f for f in os.listdir(os.path.join(self.source_dir, 'functions')) 
                             if f.endswith('.md')]) if os.path.exists(os.path.join(self.source_dir, 'functions')) else 0
        
        modules_count = len([f for f in os.listdir(os.path.join(self.source_dir, 'modules')) 
                           if f.endswith('.md')]) if has_modules else 0
        
        business_rules_count = len([f for f in os.listdir(os.path.join(self.source_dir, 'business_rules')) 
                                  if f.endswith('.md')]) if has_business_rules else 0
        
        # Get diagrams
        class_diagrams = []
        module_diagrams = []
        sequence_diagrams = []
        
        if has_diagrams:
            diagrams_dir = os.path.join(self.source_dir, 'diagrams')
            diagram_files = [f for f in os.listdir(diagrams_dir) if f.endswith('.md')]
            
            for diagram_file in diagram_files:
                diagram_path = os.path.join('diagrams', diagram_file)
                diagram_name = os.path.splitext(diagram_file)[0].replace('_', ' ').capitalize()
                
                if diagram_file.startswith('class_'):
                    class_diagrams.append({'name': diagram_name, 'path': diagram_path})
                elif diagram_file.startswith('module_'):
                    module_diagrams.append({'name': diagram_name, 'path': diagram_path})
                elif diagram_file.startswith('sequence_'):
                    sequence_diagrams.append({'name': diagram_name, 'path': diagram_path})
        
        # Common template context
        context = {
            'project_name': project_name,
            'project_description': project_description,
            'theme': 'jekyll-theme-minimal',
            'has_modules': has_modules,
            'has_diagrams': has_diagrams,
            'has_business_rules': has_business_rules,
            'classes_count': classes_count,
            'functions_count': functions_count,
            'modules_count': modules_count,
            'business_rules_count': business_rules_count,
            'class_diagrams': class_diagrams,
            'module_diagrams': module_diagrams,
            'sequence_diagrams': sequence_diagrams,
            'github_username': 'insightforge',
            'last_updated': datetime.datetime.now().strftime('%Y-%m-%d')
        }
        
        # Generate _config.yml
        config_template = env.get_template('_config.yml.j2')
        config_content = config_template.render(**context)
        
        with open(os.path.join(self.target_dir, '_config.yml'), 'w') as f:
            f.write(config_content)
        
        # Generate default layout
        default_template = env.get_template('default.html.j2')
        default_content = default_template.render(**context)
        
        with open(os.path.join(layouts_dir, 'default.html'), 'w') as f:
            f.write(default_content)
        
        # Generate README
        readme_template = env.get_template('readme.md.j2')
        readme_content = readme_template.render(**context)
        
        with open(os.path.join(self.target_dir, 'README.md'), 'w') as f:
            f.write(readme_content)
            
        # Add front matter to Markdown files
        self._add_front_matter()
    
    def _add_front_matter(self) -> None:
        """Add Jekyll front matter to Markdown files."""
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract title from content
                    title_match = re.search(r'^# (.+?)$', content, re.MULTILINE)
                    title = title_match.group(1) if title_match else os.path.splitext(file)[0]
                    
                    # Create front matter
                    front_matter = f"""---
layout: default
title: {title}
---

"""
                    
                    # Add front matter if not already present
                    if not content.startswith('---'):
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(front_matter + content)
    
    def _fix_links(self) -> None:
        """Fix internal links to work with GitHub Pages."""
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Fix Mermaid diagrams
                    content = re.sub(r'```mermaid', '{% raw %}\n```mermaid', content)
                    content = re.sub(r'```\s+(?=\n|$)', '```\n{% endraw %}', content)
                    
                    # Write updated content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
    
    def _create_docs_index(self) -> None:
        """Create an index.html file for GitHub Pages in the docs directory."""
        index_content = """---
layout: default
title: Home
---

<h1>Project Documentation</h1>

<p>Please refer to the <a href="overview.html">Overview</a> for a complete guide to this documentation.</p>

<h2>Quick Links</h2>

<ul>
  <li><a href="classes/">Classes</a></li>
  <li><a href="functions/">Functions</a></li>
  <li><a href="diagrams/">Diagrams</a></li>
</ul>
"""
        
        with open(os.path.join(self.target_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(index_content)


class GitHubPagesGenerator:
    """
    Simplified generator for GitHub Pages.
    
    This provides a streamlined way to generate GitHub Pages documentation
    from generated InsightForge documentation.
    """
    
    @staticmethod
    def generate(source_dir: str, 
                project_name: str,
                project_description: str = "",
                github_repo: Optional[str] = None,
                github_pages_dir: str = "docs",
                auto_publish: bool = False) -> str:
        """
        Generate GitHub Pages documentation.
        
        Args:
            source_dir: Directory containing generated documentation
            project_name: Name of the project
            project_description: Description of the project
            github_repo: Path to GitHub repository (None for only preparing files)
            github_pages_dir: Directory in repository for GitHub Pages
            auto_publish: Whether to automatically publish to GitHub
            
        Returns:
            Path to the exported documentation
        """
        exporter = GitHubExporter(
            source_dir=source_dir,
            github_repo_dir=github_repo,
            github_pages_dir=github_pages_dir
        )
        
        export_path = exporter.export(project_name, project_description)
        
        if auto_publish and github_repo:
            exporter.publish(branch="gh-pages")
        
        return export_path