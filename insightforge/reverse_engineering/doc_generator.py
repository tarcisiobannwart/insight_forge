"""
Documentation Generator Module
-----------------------------
Generates Markdown documentation from parsed code using the template system.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Set, Tuple

from .template_system import TemplateManager, TemplateLoader
from .diagram_generator import DiagramGenerator, DiagramIndex


class DocGenerator:
    """Generates Markdown documentation from parsed code using the template system."""
    
    def __init__(self, output_dir: str, custom_templates_dir: Optional[str] = None,
                 generate_diagrams: bool = True, max_items_per_diagram: int = 20):
        """
        Initialize with output directory and optional custom templates directory.
        
        Args:
            output_dir: Directory for output documentation
            custom_templates_dir: Optional directory with custom templates
            generate_diagrams: Whether to generate diagrams
            max_items_per_diagram: Maximum number of items to include in a diagram
        """
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.template_manager = TemplateManager(output_dir, custom_templates_dir)
        self.generate_diagrams = generate_diagrams
        
        if generate_diagrams:
            self.diagram_generator = DiagramGenerator(max_items_per_diagram)
            self.diagram_index = DiagramIndex(output_dir)
    
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
        
        # Generate diagrams if enabled
        if self.generate_diagrams:
            self._generate_diagrams(parsed_data)
        
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
        
        # If diagrams are enabled, find diagrams containing each class
        class_diagrams = {}
        if self.generate_diagrams:
            # Build a map of class name to diagrams it appears in
            for diagram in self.diagram_index.class_diagrams:
                for class_name in diagram.get('classes', []):
                    if class_name not in class_diagrams:
                        class_diagrams[class_name] = []
                    class_diagrams[class_name].append({
                        'name': diagram['name'],
                        'path': f"../{diagram['path']}"  # Path is relative to classes/
                    })
        
        for cls in classes:
            try:
                # Add diagrams to class context if available
                class_context = cls.copy()
                if cls['name'] in class_diagrams:
                    class_context['diagrams'] = class_diagrams[cls['name']]
                
                self.template_manager.render_class(class_context)
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
                
    def _generate_diagrams(self, parsed_data: Dict[str, Any]) -> None:
        """
        Generate diagrams from the parsed data.
        
        Args:
            parsed_data: Dictionary containing parsed code data
        """
        # Create diagrams directory
        diagrams_dir = os.path.join(self.output_dir, "diagrams")
        os.makedirs(diagrams_dir, exist_ok=True)
        
        # Generate class diagram
        if 'classes' in parsed_data and parsed_data['classes']:
            self._generate_class_diagrams(parsed_data)
        
        # Generate module diagram if module data is available
        if 'modules' in parsed_data and parsed_data['modules']:
            self._generate_module_diagrams(parsed_data)
        
        # Generate sequence diagrams if flow data is available
        if 'flows' in parsed_data and parsed_data['flows']:
            self._generate_sequence_diagrams(parsed_data)
        
        # Save the diagram index
        self.diagram_index.save_index()
    
    def _generate_class_diagrams(self, parsed_data: Dict[str, Any]) -> None:
        """
        Generate class diagrams from the parsed data.
        
        Args:
            parsed_data: Dictionary containing parsed code data
        """
        classes = parsed_data.get('classes', [])
        
        # If we have a lot of classes, split them into multiple diagrams
        if len(classes) > self.diagram_generator.max_items_per_diagram:
            # Group classes by module or package
            class_groups = {}
            for cls in classes:
                # Get package/module name from file path
                file_path = cls.get('file_path', '')
                module = os.path.dirname(file_path).replace('/', '.').replace('\\', '.')
                
                if not module:
                    module = 'root'
                
                if module not in class_groups:
                    class_groups[module] = []
                
                class_groups[module].append(cls)
            
            # Generate a diagram for each group
            for module, module_classes in class_groups.items():
                if not module_classes:
                    continue
                
                # Skip if just one class in the module
                if len(module_classes) == 1 and len(class_groups) > 1:
                    continue
                
                # Create diagram name
                diagram_name = f"Classes in {module}"
                file_name = f"class_diagram_{module.replace('.', '_')}.md"
                
                # Generate the diagram
                diagram_content = self.diagram_generator.generate_class_diagram(
                    {'classes': module_classes},
                    include_methods=True,
                    include_attributes=True
                )
                
                # Save the diagram
                diagram_path = os.path.join(self.output_dir, "diagrams", file_name)
                diagram_rel_path = os.path.join("diagrams", file_name)
                
                # Prepare context for template
                context = {
                    'diagram_name': diagram_name,
                    'diagram_content': diagram_content,
                    'classes': module_classes,
                    'diagram_description': f"Class diagram showing classes in the {module} module."
                }
                
                # Render and save the diagram document
                try:
                    content = self.template_manager.loader.render_template(
                        "class_diagram.md.j2", context)
                    
                    with open(diagram_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Add to index
                    self.diagram_index.add_class_diagram(
                        diagram_name,
                        diagram_rel_path,
                        [cls['name'] for cls in module_classes]
                    )
                    
                    self.logger.debug(f"Generated class diagram for {module}")
                except Exception as e:
                    self.logger.error(f"Error generating class diagram for {module}: {str(e)}")
            
            # Generate main diagram with all classes but without methods/attributes
            if len(class_groups) > 1:
                main_diagram_content = self.diagram_generator.generate_class_diagram(
                    parsed_data,
                    include_methods=False,
                    include_attributes=False
                )
                
                # Save the main diagram
                main_diagram_path = os.path.join(self.output_dir, "diagrams", "class_diagram_main.md")
                main_diagram_rel_path = os.path.join("diagrams", "class_diagram_main.md")
                
                # Prepare context for template
                context = {
                    'diagram_name': "Main Class Diagram",
                    'diagram_content': main_diagram_content,
                    'classes': classes,
                    'diagram_description': "Overview diagram showing all classes and their relationships.",
                    'notes': "This diagram shows only class relationships. For detailed class structure, see the module-specific diagrams."
                }
                
                # Render and save the main diagram document
                try:
                    content = self.template_manager.loader.render_template(
                        "class_diagram.md.j2", context)
                    
                    with open(main_diagram_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Add to index
                    self.diagram_index.add_class_diagram(
                        "Main Class Diagram",
                        main_diagram_rel_path,
                        [cls['name'] for cls in classes]
                    )
                    
                    self.logger.debug(f"Generated main class diagram")
                except Exception as e:
                    self.logger.error(f"Error generating main class diagram: {str(e)}")
        else:
            # Just generate one diagram for all classes
            diagram_content = self.diagram_generator.generate_class_diagram(
                parsed_data,
                include_methods=True,
                include_attributes=True
            )
            
            # Save the diagram
            diagram_path = os.path.join(self.output_dir, "diagrams", "class_diagram.md")
            diagram_rel_path = os.path.join("diagrams", "class_diagram.md")
            
            # Prepare context for template
            context = {
                'diagram_name': "Class Diagram",
                'diagram_content': diagram_content,
                'classes': classes,
                'diagram_description': "Class diagram showing all classes and their relationships."
            }
            
            # Render and save the diagram document
            try:
                content = self.template_manager.loader.render_template(
                    "class_diagram.md.j2", context)
                
                with open(diagram_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Add to index
                self.diagram_index.add_class_diagram(
                    "Class Diagram",
                    diagram_rel_path,
                    [cls['name'] for cls in classes]
                )
                
                self.logger.debug(f"Generated class diagram")
            except Exception as e:
                self.logger.error(f"Error generating class diagram: {str(e)}")
    
    def _generate_module_diagrams(self, parsed_data: Dict[str, Any]) -> None:
        """
        Generate module diagrams from the parsed data.
        
        Args:
            parsed_data: Dictionary containing parsed code data
        """
        modules = parsed_data.get('modules', [])
        
        # Generate module diagram
        diagram_content = self.diagram_generator.generate_module_diagram(
            parsed_data,
            group_by_package=True
        )
        
        # Save the diagram
        diagram_path = os.path.join(self.output_dir, "diagrams", "module_diagram.md")
        diagram_rel_path = os.path.join("diagrams", "module_diagram.md")
        
        # Prepare context for template
        context = {
            'diagram_name': "Module Dependencies",
            'diagram_content': diagram_content,
            'modules': modules,
            'diagram_description': "Diagram showing module dependencies."
        }
        
        # Render and save the diagram document
        try:
            content = self.template_manager.loader.render_template(
                "module_diagram.md.j2", context)
            
            with open(diagram_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Add to index
            self.diagram_index.add_module_diagram(
                "Module Dependencies",
                diagram_rel_path,
                [m['name'] for m in modules]
            )
            
            self.logger.debug(f"Generated module diagram")
        except Exception as e:
            self.logger.error(f"Error generating module diagram: {str(e)}")
    
    def _generate_sequence_diagrams(self, parsed_data: Dict[str, Any]) -> None:
        """
        Generate sequence diagrams from the parsed data.
        
        Args:
            parsed_data: Dictionary containing parsed code data
        """
        flows = parsed_data.get('flows', {})
        
        # Generate sequence diagram for each flow
        for flow_name, flow in flows.items():
            # Skip empty or invalid flows
            if not flow:
                continue
            
            # Generate diagram
            diagram_content = self.diagram_generator.generate_sequence_diagram(
                parsed_data,
                flow_name
            )
            
            # Create safe filename
            file_name = f"sequence_{flow_name.replace(' ', '_').lower()}.md"
            
            # Save the diagram
            diagram_path = os.path.join(self.output_dir, "diagrams", file_name)
            diagram_rel_path = os.path.join("diagrams", file_name)
            
            # Prepare context for template
            context = {
                'diagram_name': f"Sequence: {flow_name}",
                'diagram_content': diagram_content,
                'flow': flow_name,
                'flow_description': flow.get('description', ''),
                'components': flow.get('participants', []),
                'diagram_description': f"Sequence diagram for the {flow_name} flow."
            }
            
            # Render and save the diagram document
            try:
                content = self.template_manager.loader.render_template(
                    "sequence_diagram.md.j2", context)
                
                with open(diagram_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Add to index
                self.diagram_index.add_sequence_diagram(
                    f"Sequence: {flow_name}",
                    diagram_rel_path,
                    flow_name
                )
                
                self.logger.debug(f"Generated sequence diagram for {flow_name}")
            except Exception as e:
                self.logger.error(f"Error generating sequence diagram for {flow_name}: {str(e)}")
    
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