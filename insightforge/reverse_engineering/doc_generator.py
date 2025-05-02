"""
Documentation Generator Module
-----------------------------
Generates Markdown documentation from parsed code using the template system.
"""

import os
import logging
from typing import Dict, Any, List, Optional

from .template_system import TemplateManager, TemplateLoader


class DocGenerator:
    """Generates Markdown documentation from parsed code using the template system."""
    
    def __init__(self, output_dir: str, custom_templates_dir: Optional[str] = None):
        """
        Initialize with output directory and optional custom templates directory.
        
        Args:
            output_dir: Directory for output documentation
            custom_templates_dir: Optional directory with custom templates
        """
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.template_manager = TemplateManager(output_dir, custom_templates_dir)
    
    def generate(self, parsed_data: Dict[str, Any], project_name: str = "Project", 
                project_description: str = "") -> None:
        """
        Generate documentation from parsed data.
        
        Args:
            parsed_data: Dictionary containing parsed code data
            project_name: Name of the project for the index document
            project_description: Description of the project for the index document
        """
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Generate overview and index
        self._generate_overview(parsed_data)
        self._generate_index(parsed_data, project_name, project_description)
        
        # Generate class documentation
        if 'classes' in parsed_data:
            self._generate_class_docs(parsed_data['classes'])
        
        # Generate function documentation
        if 'functions' in parsed_data:
            self._generate_function_docs(parsed_data['functions'])
            
        # Generate business rules documentation
        if 'business_rules' in parsed_data:
            self._generate_business_rule_docs(parsed_data['business_rules'])
    
    def _generate_overview(self, parsed_data: Dict[str, Any]) -> None:
        """
        Generate an overview document.
        
        Args:
            parsed_data: Dictionary containing parsed code data
        """
        try:
            self.template_manager.render_overview(parsed_data)
            self.logger.info("Generated overview document")
        except Exception as e:
            self.logger.error(f"Error generating overview: {str(e)}")
            raise
    
    def _generate_index(self, parsed_data: Dict[str, Any], project_name: str, 
                       project_description: str) -> None:
        """
        Generate an index document.
        
        Args:
            parsed_data: Dictionary containing parsed code data
            project_name: Name of the project
            project_description: Description of the project
        """
        try:
            self.template_manager.render_index(parsed_data, project_name, project_description)
            self.logger.info("Generated index document")
        except Exception as e:
            self.logger.error(f"Error generating index: {str(e)}")
            raise
    
    def _generate_class_docs(self, classes: List[Dict[str, Any]]) -> None:
        """
        Generate documentation for classes.
        
        Args:
            classes: List of class data dictionaries
        """
        # Create classes directory
        classes_dir = os.path.join(self.output_dir, "classes")
        os.makedirs(classes_dir, exist_ok=True)
        
        for cls in classes:
            try:
                self.template_manager.render_class(cls)
                self.logger.debug(f"Generated documentation for class {cls['name']}")
            except Exception as e:
                self.logger.error(f"Error generating docs for class {cls.get('name', 'unknown')}: {str(e)}")
    
    def _generate_function_docs(self, functions: List[Dict[str, Any]]) -> None:
        """
        Generate documentation for functions.
        
        Args:
            functions: List of function data dictionaries
        """
        # Create functions directory
        functions_dir = os.path.join(self.output_dir, "functions")
        os.makedirs(functions_dir, exist_ok=True)
        
        for func in functions:
            try:
                self.template_manager.render_function(func)
                self.logger.debug(f"Generated documentation for function {func['name']}")
            except Exception as e:
                self.logger.error(f"Error generating docs for function {func.get('name', 'unknown')}: {str(e)}")
    
    def _generate_business_rule_docs(self, rules: List[Dict[str, Any]]) -> None:
        """
        Generate documentation for business rules.
        
        Args:
            rules: List of business rule data dictionaries
        """
        # Create business_rules directory
        rules_dir = os.path.join(self.output_dir, "business_rules")
        os.makedirs(rules_dir, exist_ok=True)
        
        for rule in rules:
            try:
                self.template_manager.render_business_rule(rule)
                self.logger.debug(f"Generated documentation for business rule {rule['id']}")
            except Exception as e:
                self.logger.error(f"Error generating docs for rule {rule.get('id', 'unknown')}: {str(e)}")
                
    def customize_template(self, template_name: str, custom_template_content: str) -> bool:
        """
        Create or update a custom template.
        
        Args:
            template_name: Name of the template (e.g., "class.md.j2")
            custom_template_content: Content for the custom template
            
        Returns:
            True if successful, False otherwise
        """
        custom_dir = self.template_manager.loader.custom_dir
        
        if not custom_dir:
            # Use a default custom templates directory in the output directory
            custom_dir = os.path.join(self.output_dir, "_templates")
            os.makedirs(custom_dir, exist_ok=True)
            
            # Update the template loader with the new custom directory
            self.template_manager.loader.custom_dir = custom_dir
            
            # Recreate the loader with the new custom directory
            self.template_manager.loader = TemplateLoader(custom_dir)
        
        try:
            # Ensure the custom directory exists
            os.makedirs(custom_dir, exist_ok=True)
            
            # Write the custom template
            template_path = os.path.join(custom_dir, template_name)
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(custom_template_content)
                
            return True
        except Exception as e:
            self.logger.error(f"Error creating custom template: {str(e)}")
            return False