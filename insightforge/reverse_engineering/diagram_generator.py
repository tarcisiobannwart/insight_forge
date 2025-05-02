"""
Diagram Generator Module
----------------------
Generates Mermaid diagrams from parsed code.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Set, Tuple


class DiagramGenerator:
    """
    Generates Mermaid diagrams from parsed code data.
    
    This class provides methods to create various types of diagrams:
    - Class diagrams showing inheritance and relations
    - Module/package diagrams showing dependencies
    - Sequence diagrams for interaction flows
    """
    
    def __init__(self, max_items_per_diagram: int = 20):
        """
        Initialize the diagram generator.
        
        Args:
            max_items_per_diagram: Maximum number of items to include in a diagram
                before splitting it (to prevent overly complex diagrams)
        """
        self.logger = logging.getLogger(__name__)
        self.max_items_per_diagram = max_items_per_diagram
    
    def generate_class_diagram(self, parsed_data: Dict[str, Any], 
                             include_methods: bool = True,
                             include_attributes: bool = True,
                             include_private: bool = False,
                             max_methods: int = 5,
                             filter_classes: Optional[List[str]] = None) -> str:
        """
        Generate a Mermaid class diagram from parsed data.
        
        Args:
            parsed_data: Dictionary containing parsed code data
            include_methods: Whether to include methods in the diagram
            include_attributes: Whether to include attributes in the diagram
            include_private: Whether to include private members (prefixed with _)
            max_methods: Maximum number of methods to display per class
            filter_classes: List of class names to include (None for all)
            
        Returns:
            Mermaid diagram syntax as string
        """
        if 'classes' not in parsed_data or not parsed_data['classes']:
            return "```mermaid\nclassDiagram\n  class NoClasses\n```"
        
        classes = parsed_data['classes']
        
        # Filter classes if specified
        if filter_classes:
            classes = [cls for cls in classes if cls['name'] in filter_classes]
        
        # Check if we need to split the diagram
        if len(classes) > self.max_items_per_diagram:
            self.logger.warning(
                f"Class diagram has {len(classes)} classes, which exceeds the maximum "
                f"of {self.max_items_per_diagram}. The diagram may be complex."
            )
        
        # Start building the diagram
        diagram = ["```mermaid", "classDiagram"]
        
        # Add inheritance relationships
        relationships = []
        for cls in classes:
            if 'base_classes' in cls and cls['base_classes']:
                for base in cls['base_classes']:
                    # Skip external base classes if complex inheritance
                    if base in [c['name'] for c in classes]:
                        relationships.append(f"  {base} <|-- {cls['name']} : extends")
        
        # Add other relationships (if available)
        if 'relationships' in parsed_data:
            for rel in parsed_data.get('relationships', []):
                source = rel.get('source')
                target = rel.get('target')
                rel_type = rel.get('type', 'association')
                
                if source and target:
                    if rel_type == 'composition':
                        relationships.append(f"  {source} *-- {target} : contains")
                    elif rel_type == 'aggregation':
                        relationships.append(f"  {source} o-- {target} : has")
                    elif rel_type == 'dependency':
                        relationships.append(f"  {source} --> {target} : uses")
                    else:  # association
                        relationships.append(f"  {source} -- {target} : relates to")
        
        # Add all relationships
        diagram.extend(relationships)
        
        # Add class details
        for cls in classes:
            class_lines = []
            
            # Start class definition
            class_lines.append(f"  class {cls['name']} {{")
            
            # Add attributes
            if include_attributes and 'attributes' in cls:
                attributes = cls.get('attributes', [])
                for attr in attributes:
                    # Skip private attributes if not including private
                    if not include_private and attr.get('name', '').startswith('_'):
                        continue
                    
                    attr_name = attr.get('name', '')
                    attr_type = attr.get('type', '')
                    
                    # Format the attribute with type if available
                    if attr_type:
                        class_lines.append(f"    +{attr_name} : {attr_type}")
                    else:
                        class_lines.append(f"    +{attr_name}")
            
            # Add methods
            if include_methods and 'methods' in cls:
                methods = cls.get('methods', [])
                # Filter private methods if necessary
                if not include_private:
                    methods = [m for m in methods if not m.get('name', '').startswith('_')]
                
                # Respect max methods limit
                methods = methods[:max_methods]
                
                for method in methods:
                    method_name = method.get('name', '')
                    params = method.get('parameters', [])
                    return_type = method.get('return_type', '')
                    
                    # Format method with parameters and return type
                    param_str = ", ".join(params)
                    if return_type:
                        class_lines.append(f"    +{method_name}({param_str}) : {return_type}")
                    else:
                        class_lines.append(f"    +{method_name}({param_str})")
            
            # Close class definition
            class_lines.append("  }")
            
            # Add class to diagram
            diagram.extend(class_lines)
        
        # Close diagram
        diagram.append("```")
        
        return "\n".join(diagram)
    
    def generate_module_diagram(self, parsed_data: Dict[str, Any],
                              group_by_package: bool = True,
                              include_external: bool = False) -> str:
        """
        Generate a Mermaid module/package diagram from parsed data.
        
        Args:
            parsed_data: Dictionary containing parsed code data
            group_by_package: Whether to group modules by package
            include_external: Whether to include external dependencies
            
        Returns:
            Mermaid diagram syntax as string
        """
        if 'modules' not in parsed_data or not parsed_data['modules']:
            return "```mermaid\ngraph TD\n  NoModules[No modules found]\n```"
        
        modules = parsed_data.get('modules', [])
        
        # Start building the diagram
        diagram = ["```mermaid", "graph TD"]
        
        # Add subgraphs for packages if grouping
        if group_by_package:
            packages = {}
            
            # Group modules by package
            for module in modules:
                package = self._get_package_name(module.get('name', ''))
                if package not in packages:
                    packages[package] = []
                packages[package].append(module)
            
            # Add subgraphs for each package
            for package, pkg_modules in packages.items():
                diagram.append(f"  subgraph {package}")
                
                # Add module nodes
                for module in pkg_modules:
                    module_id = self._clean_id(module.get('name', ''))
                    module_name = module.get('name', '').split('.')[-1]
                    diagram.append(f"    {module_id}[{module_name}]")
                
                diagram.append("  end")
        else:
            # Add all modules as nodes
            for module in modules:
                module_id = self._clean_id(module.get('name', ''))
                module_name = module.get('name', '')
                diagram.append(f"  {module_id}[{module_name}]")
        
        # Add dependencies between modules
        if 'dependencies' in parsed_data:
            for dep in parsed_data.get('dependencies', []):
                source = dep.get('source')
                target = dep.get('target')
                
                # Skip external dependencies if not included
                if not include_external and (self._is_external(source) or self._is_external(target)):
                    continue
                
                source_id = self._clean_id(source)
                target_id = self._clean_id(target)
                
                diagram.append(f"  {source_id} --> {target_id}")
        
        # Close diagram
        diagram.append("```")
        
        return "\n".join(diagram)
    
    def generate_sequence_diagram(self, parsed_data: Dict[str, Any],
                                flow_name: str,
                                max_depth: int = 5) -> str:
        """
        Generate a Mermaid sequence diagram for a specific flow.
        
        Args:
            parsed_data: Dictionary containing parsed code data
            flow_name: Name of the flow to diagram
            max_depth: Maximum depth of calls to include
            
        Returns:
            Mermaid diagram syntax as string
        """
        # This is a simplified placeholder implementation
        # Actual sequence diagram generation would require call graph analysis
        
        flows = parsed_data.get('flows', {})
        flow = flows.get(flow_name)
        
        if not flow:
            return f"```mermaid\nsequenceDiagram\n  Note over System: Flow '{flow_name}' not found\n```"
        
        # Start building the diagram
        diagram = ["```mermaid", "sequenceDiagram"]
        
        # Add participants
        participants = flow.get('participants', [])
        for participant in participants:
            diagram.append(f"  participant {participant}")
        
        # Add sequence steps
        steps = flow.get('steps', [])
        for step in steps:
            source = step.get('source', 'User')
            target = step.get('target', 'System')
            message = step.get('message', '')
            
            diagram.append(f"  {source}->>+{target}: {message}")
            
            # Add response if available
            response = step.get('response')
            if response:
                diagram.append(f"  {target}-->>-{source}: {response}")
        
        # Close diagram
        diagram.append("```")
        
        return "\n".join(diagram)
    
    def _clean_id(self, name: str) -> str:
        """
        Clean a name to be used as an ID in a Mermaid diagram.
        
        Args:
            name: Original name
            
        Returns:
            Cleaned ID string
        """
        # Replace characters that cause issues in Mermaid IDs
        clean = name.replace('.', '_').replace('-', '_').replace(' ', '_')
        return clean
    
    def _get_package_name(self, module_name: str) -> str:
        """
        Extract the package name from a module name.
        
        Args:
            module_name: Full module name
            
        Returns:
            Package name
        """
        parts = module_name.split('.')
        if len(parts) <= 1:
            return 'root'
        return parts[0]
    
    def _is_external(self, module_name: str) -> bool:
        """
        Check if a module is external to the project.
        
        Args:
            module_name: Module name to check
            
        Returns:
            True if the module is external
        """
        # This is a basic check that can be improved with project-specific logic
        standard_libs = {'os', 'sys', 'math', 're', 'datetime', 'collections',
                         'json', 'csv', 'logging', 'random', 'time', 'unittest',
                         'typing', 'pathlib', 'shutil', 'functools', 'itertools'}
        
        first_part = module_name.split('.')[0]
        return first_part in standard_libs


class DiagramIndex:
    """Manages an index of diagrams for navigation."""
    
    def __init__(self, output_dir: str):
        """
        Initialize the diagram index.
        
        Args:
            output_dir: Directory where diagrams are stored
        """
        self.output_dir = output_dir
        self.class_diagrams = []
        self.module_diagrams = []
        self.sequence_diagrams = []
    
    def add_class_diagram(self, name: str, path: str, classes: List[str]) -> None:
        """
        Add a class diagram to the index.
        
        Args:
            name: Name of the diagram
            path: Path to the diagram file, relative to output_dir
            classes: List of classes included in the diagram
        """
        self.class_diagrams.append({
            'name': name,
            'path': path,
            'classes': classes
        })
    
    def add_module_diagram(self, name: str, path: str, modules: List[str]) -> None:
        """
        Add a module diagram to the index.
        
        Args:
            name: Name of the diagram
            path: Path to the diagram file, relative to output_dir
            modules: List of modules included in the diagram
        """
        self.module_diagrams.append({
            'name': name,
            'path': path,
            'modules': modules
        })
    
    def add_sequence_diagram(self, name: str, path: str, flow: str) -> None:
        """
        Add a sequence diagram to the index.
        
        Args:
            name: Name of the diagram
            path: Path to the diagram file, relative to output_dir
            flow: Name of the flow represented
        """
        self.sequence_diagrams.append({
            'name': name,
            'path': path,
            'flow': flow
        })
    
    def generate_index_markdown(self) -> str:
        """
        Generate a Markdown index of all diagrams.
        
        Returns:
            Markdown content for the index
        """
        lines = ["# Diagram Index", ""]
        
        # Class diagrams
        if self.class_diagrams:
            lines.append("## Class Diagrams")
            lines.append("")
            for diagram in self.class_diagrams:
                lines.append(f"- [{diagram['name']}]({diagram['path']})")
            lines.append("")
        
        # Module diagrams
        if self.module_diagrams:
            lines.append("## Module Diagrams")
            lines.append("")
            for diagram in self.module_diagrams:
                lines.append(f"- [{diagram['name']}]({diagram['path']})")
            lines.append("")
        
        # Sequence diagrams
        if self.sequence_diagrams:
            lines.append("## Sequence Diagrams")
            lines.append("")
            for diagram in self.sequence_diagrams:
                lines.append(f"- [{diagram['name']}]({diagram['path']})")
            lines.append("")
        
        return "\n".join(lines)
    
    def save_index(self) -> str:
        """
        Save the diagram index to a file.
        
        Returns:
            Path to the saved index file
        """
        os.makedirs(os.path.join(self.output_dir, "diagrams"), exist_ok=True)
        
        index_path = os.path.join(self.output_dir, "diagrams", "index.md")
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_index_markdown())
        
        return index_path