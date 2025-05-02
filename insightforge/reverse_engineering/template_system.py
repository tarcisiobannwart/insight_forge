"""
Template System Module
---------------------
Provides a flexible template system for documentation generation.
"""

import os
import re
import logging
from typing import Dict, Any, List, Optional, Callable, Union

import jinja2


class TemplateLoader:
    """Template loading and rendering system for documentation generation."""
    
    def __init__(self, custom_dir: Optional[str] = None):
        """
        Initialize the template loader.
        
        Args:
            custom_dir: Optional path to custom templates directory
        """
        self.logger = logging.getLogger(__name__)
        self.custom_dir = custom_dir
        self.default_dir = os.path.join(os.path.dirname(__file__), "templates")
        
        # Set up the Jinja2 environment with template inheritance support
        loaders = []
        if self.custom_dir and os.path.isdir(self.custom_dir):
            loaders.append(jinja2.FileSystemLoader(self.custom_dir))
        
        loaders.append(jinja2.FileSystemLoader(self.default_dir))
        
        self.env = jinja2.Environment(
            loader=jinja2.ChoiceLoader(loaders),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        # Add custom filters and functions
        self._register_filters()
        self._register_globals()
    
    def _register_filters(self) -> None:
        """Register custom filters for templates."""
        self.env.filters["markdown_escape"] = self._markdown_escape
        self.env.filters["pluralize"] = self._pluralize
        self.env.filters["format_code"] = self._format_code_block
        self.env.filters["titleize"] = self._titleize
    
    def _register_globals(self) -> None:
        """Register global functions available to all templates."""
        self.env.globals["include_file"] = self._include_file
    
    def get_template(self, name: str) -> jinja2.Template:
        """
        Get a template by name.
        
        Args:
            name: Template name (e.g., "class.md.j2")
            
        Returns:
            Jinja2 Template object
            
        Raises:
            ValueError: If template not found
        """
        try:
            return self.env.get_template(name)
        except jinja2.exceptions.TemplateNotFound:
            raise ValueError(f"Template '{name}' not found")
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_name: Template name (e.g., "class.md.j2")
            context: Data context for template rendering
            
        Returns:
            Rendered template as string
            
        Raises:
            ValueError: If template not found or rendering fails
        """
        try:
            template = self.get_template(template_name)
            return template.render(**context)
        except jinja2.exceptions.TemplateError as e:
            self.logger.error(f"Error rendering template '{template_name}': {str(e)}")
            raise ValueError(f"Failed to render template '{template_name}': {str(e)}")
    
    def list_templates(self) -> List[str]:
        """
        List all available templates.
        
        Returns:
            List of template names
        """
        return [t for t in self.env.list_templates() if not t.startswith("partials/")]
    
    def template_exists(self, name: str) -> bool:
        """
        Check if a template exists.
        
        Args:
            name: Template name to check
            
        Returns:
            True if template exists, False otherwise
        """
        try:
            self.env.get_template(name)
            return True
        except jinja2.exceptions.TemplateNotFound:
            return False
    
    # Custom filters
    
    @staticmethod
    def _markdown_escape(text: str) -> str:
        """
        Escape special Markdown characters.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        if not text:
            return ""
        
        # Characters to escape in markdown
        for char in ["\\", "`", "*", "_", "{", "}", "[", "]", "(", ")", "#", "+", "-", ".", "!"]:
            text = text.replace(char, f"\\{char}")
        
        return text
    
    @staticmethod
    def _pluralize(word: str, count: int) -> str:
        """
        Pluralize a word based on count.
        
        Args:
            word: Word to pluralize
            count: Count to determine pluralization
            
        Returns:
            Pluralized word if count != 1
        """
        if count == 1:
            return word
        
        # Simple English pluralization rules
        if word.endswith('s') or word.endswith('x') or word.endswith('z') or \
           word.endswith('ch') or word.endswith('sh'):
            return word + 'es'
        elif word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
            return word[:-1] + 'ies'
        else:
            return word + 's'
    
    @staticmethod
    def _format_code_block(code: str, language: str = "python") -> str:
        """
        Format text as a Markdown code block.
        
        Args:
            code: Code text
            language: Programming language for syntax highlighting
            
        Returns:
            Formatted code block
        """
        if not code:
            return ""
        
        return f"```{language}\n{code}\n```"
    
    @staticmethod
    def _titleize(text: str) -> str:
        """
        Convert text to title case, preserving common acronyms.
        
        Args:
            text: Text to convert
            
        Returns:
            Title-cased text
        """
        if not text:
            return ""
        
        # Keep common acronyms uppercase
        acronyms = ["API", "UI", "URL", "ID", "HTML", "XML", "JSON", "HTTP", "SDK"]
        words = text.split()
        
        result = []
        for word in words:
            if word.upper() in acronyms:
                result.append(word.upper())
            else:
                result.append(word.capitalize())
        
        return " ".join(result)
    
    # Template globals
    
    @staticmethod
    def _include_file(filename: str) -> str:
        """
        Include a file's contents in a template.
        
        Args:
            filename: Path to file to include
            
        Returns:
            File contents as string or empty string if file not found
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except (FileNotFoundError, IOError):
            return ""


class TemplateManager:
    """
    Manages template rendering and output for different documentation types.
    
    This class provides a higher-level interface over the TemplateLoader,
    handling template selection, output file paths, and template context.
    """
    
    def __init__(self, output_dir: str, custom_templates_dir: Optional[str] = None):
        """
        Initialize the template manager.
        
        Args:
            output_dir: Directory for generated documentation
            custom_templates_dir: Optional path to custom templates
        """
        self.output_dir = output_dir
        self.loader = TemplateLoader(custom_templates_dir)
        self.logger = logging.getLogger(__name__)
    
    def render_class(self, class_data: Dict[str, Any], output_subdir: str = "classes") -> str:
        """
        Render documentation for a class.
        
        Args:
            class_data: Class data dictionary
            output_subdir: Subdirectory for output file
            
        Returns:
            Path to generated file
        """
        template_name = "class.md.j2"
        context = {"class": class_data}
        
        output_dir = os.path.join(self.output_dir, output_subdir)
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{class_data['name']}.md")
        
        try:
            content = self.loader.render_template(template_name, context)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return output_path
        except Exception as e:
            self.logger.error(f"Error rendering class template: {str(e)}")
            raise
    
    def render_function(self, function_data: Dict[str, Any], output_subdir: str = "functions") -> str:
        """
        Render documentation for a function.
        
        Args:
            function_data: Function data dictionary
            output_subdir: Subdirectory for output file
            
        Returns:
            Path to generated file
        """
        template_name = "function.md.j2"
        context = {"function": function_data}
        
        output_dir = os.path.join(self.output_dir, output_subdir)
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{function_data['name']}.md")
        
        try:
            content = self.loader.render_template(template_name, context)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return output_path
        except Exception as e:
            self.logger.error(f"Error rendering function template: {str(e)}")
            raise
    
    def render_business_rule(self, rule_data: Dict[str, Any], output_subdir: str = "business_rules") -> str:
        """
        Render documentation for a business rule.
        
        Args:
            rule_data: Business rule data dictionary
            output_subdir: Subdirectory for output file
            
        Returns:
            Path to generated file
        """
        template_name = "businessrule.md.j2"
        context = {"rule": rule_data}
        
        output_dir = os.path.join(self.output_dir, output_subdir)
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{rule_data['id']}.md")
        
        try:
            content = self.loader.render_template(template_name, context)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return output_path
        except Exception as e:
            self.logger.error(f"Error rendering business rule template: {str(e)}")
            raise
    
    def render_overview(self, parsed_data: Dict[str, Any]) -> str:
        """
        Render project overview documentation.
        
        Args:
            parsed_data: All parsed project data
            
        Returns:
            Path to generated file
        """
        template_name = "overview.md.j2"
        
        # Prepare context with expected attributes
        context = {
            "classes": parsed_data.get("classes", []),
            "functions": parsed_data.get("functions", []),
            "business_rules": parsed_data.get("business_rules", []),
            "usecases": parsed_data.get("usecases", []),
            "userstories": parsed_data.get("userstories", [])
        }
        
        output_path = os.path.join(self.output_dir, "overview.md")
        
        try:
            content = self.loader.render_template(template_name, context)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return output_path
        except Exception as e:
            self.logger.error(f"Error rendering overview template: {str(e)}")
            raise
    
    def render_index(self, parsed_data: Dict[str, Any], project_name: str = "Project", 
                   project_description: str = "") -> str:
        """
        Render main index documentation.
        
        Args:
            parsed_data: All parsed project data
            project_name: Name of the project
            project_description: Description of the project
            
        Returns:
            Path to generated file
        """
        template_name = "index.md.j2"
        
        # Prepare context with expected attributes
        context = {
            "project_name": project_name,
            "project_description": project_description,
            "classes": parsed_data.get("classes", []),
            "functions": parsed_data.get("functions", []),
            "business_rules": parsed_data.get("business_rules", []),
            "usecases": parsed_data.get("usecases", []),
            "userstories": parsed_data.get("userstories", []),
            "has_diagrams": os.path.exists(os.path.join(self.output_dir, "diagrams"))
        }
        
        output_path = os.path.join(self.output_dir, "index.md")
        
        try:
            content = self.loader.render_template(template_name, context)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return output_path
        except Exception as e:
            self.logger.error(f"Error rendering index template: {str(e)}")
            raise
            
    def render_diagram(self, diagram_type: str, context: Dict[str, Any]) -> str:
        """
        Render diagram documentation.
        
        Args:
            diagram_type: Type of diagram ("class", "module", "sequence")
            context: Diagram data
            
        Returns:
            Path to generated file
        """
        template_map = {
            "class": "class_diagram.md.j2",
            "module": "module_diagram.md.j2",
            "sequence": "sequence_diagram.md.j2",
            "index": "diagram_index.md.j2"
        }
        
        if diagram_type not in template_map:
            raise ValueError(f"Unknown diagram type: {diagram_type}")
            
        template_name = template_map[diagram_type]
        
        # Determine output path
        if "output_path" in context:
            output_path = context["output_path"]
        else:
            diagrams_dir = os.path.join(self.output_dir, "diagrams")
            os.makedirs(diagrams_dir, exist_ok=True)
            
            # Default filename based on diagram type and name
            diagram_name = context.get("diagram_name", "diagram").lower().replace(" ", "_")
            output_path = os.path.join(diagrams_dir, f"{diagram_type}_{diagram_name}.md")
        
        try:
            content = self.loader.render_template(template_name, context)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return output_path
        except Exception as e:
            self.logger.error(f"Error rendering {diagram_type} diagram template: {str(e)}")
            raise