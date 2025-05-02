"""
Diagram Generator Module
----------------------
Generates Mermaid diagrams from parsed code.
"""

import os
import logging
import re
from typing import Dict, List, Any, Optional, Set, Tuple

from .relationship_detector import (
    RelationshipDetector, 
    PhpRelationshipDetector, 
    JavaScriptRelationshipDetector
)
from .flow_analyzer import (
    FlowAnalyzer,
    PythonFlowAnalyzer,
    GenericFlowAnalyzer
)


class DiagramGenerator:
    """
    Generates Mermaid diagrams from parsed code data.
    
    This class provides methods to create various types of diagrams:
    - Class diagrams showing inheritance and relations
    - Module/package diagrams showing dependencies
    - Sequence diagrams for interaction flows
    """
    
    def __init__(self, max_items_per_diagram: int = 20, detect_relationships: bool = True):
        """
        Initialize the diagram generator.
        
        Args:
            max_items_per_diagram: Maximum number of items to include in a diagram
                before splitting it (to prevent overly complex diagrams)
            detect_relationships: Whether to automatically detect relationships
        """
        self.logger = logging.getLogger(__name__)
        self.max_items_per_diagram = max_items_per_diagram
        self.detect_relationships = detect_relationships
        
        # Store parsed data for reference by doc generator
        self.parsed_data = {}
        
        # Initialize relationship detectors
        self.relationship_detector = RelationshipDetector()
        self.php_relationship_detector = PhpRelationshipDetector()
        self.javascript_relationship_detector = JavaScriptRelationshipDetector()
        
        # Initialize flow analyzers
        self.python_flow_analyzer = PythonFlowAnalyzer()
        self.generic_flow_analyzer = GenericFlowAnalyzer()
    
    def generate_class_diagram(self, parsed_data: Dict[str, Any], 
                             include_methods: bool = True,
                             include_attributes: bool = True,
                             include_private: bool = False,
                             max_methods: int = 5,
                             filter_classes: Optional[List[str]] = None,
                             languages: Optional[List[str]] = None) -> str:
        """
        Generate a Mermaid class diagram from parsed data.
        
        Args:
            parsed_data: Dictionary containing parsed code data
            include_methods: Whether to include methods in the diagram
            include_attributes: Whether to include attributes in the diagram
            include_private: Whether to include private members (prefixed with _)
            max_methods: Maximum number of methods to display per class
            filter_classes: List of class names to include (None for all)
            languages: List of languages to include (None for all)
            
        Returns:
            Mermaid diagram syntax as string
        """
        if 'classes' not in parsed_data or not parsed_data['classes']:
            return "```mermaid\nclassDiagram\n  class NoClasses\n```"
        
        # Make a copy of the data to avoid modifying the original
        data = {key: value for key, value in parsed_data.items()}
        classes = data['classes']
        
        # Filter classes by language if specified
        if languages:
            classes = []
            for cls in parsed_data['classes']:
                # Extract language from file extension
                file_path = cls.get('file_path', '')
                if file_path:
                    ext = os.path.splitext(file_path)[1].lower()
                    language = None
                    
                    if ext == '.py':
                        language = 'python'
                    elif ext == '.php':
                        language = 'php'
                    elif ext in ['.js', '.jsx']:
                        language = 'javascript'
                    elif ext in ['.ts', '.tsx']:
                        language = 'typescript'
                    
                    if language and language in languages:
                        classes.append(cls)
                else:
                    # If no file path, include it (could be from a language-specific parser)
                    classes.append(cls)
            
            data['classes'] = classes
        
        # Filter classes by name if specified
        if filter_classes:
            classes = [cls for cls in classes if cls['name'] in filter_classes]
            data['classes'] = classes
        
        # Detect relationships if enabled
        if self.detect_relationships and 'relationships' not in data:
            # Apply appropriate relationship detector based on file extensions
            data = self.relationship_detector.detect_relationships(data)
            
            # Apply language-specific relationship detectors
            # Check if there are PHP classes
            php_classes = [cls for cls in classes if cls.get('file_path', '').endswith('.php')]
            if php_classes:
                php_data = {key: value for key, value in data.items()}
                php_data['classes'] = php_classes
                php_data = self.php_relationship_detector.detect_relationships(php_data)
                
                # Merge relationships back
                for rel in php_data.get('relationships', []):
                    if rel not in data['relationships']:
                        data['relationships'].append(rel)
            
            # Check if there are JavaScript/TypeScript classes
            js_ts_classes = [cls for cls in classes if cls.get('file_path', '').endswith(('.js', '.jsx', '.ts', '.tsx'))]
            if js_ts_classes:
                js_data = {key: value for key, value in data.items()}
                js_data['classes'] = js_ts_classes
                js_data = self.javascript_relationship_detector.detect_relationships(js_data)
                
                # Merge relationships back
                for rel in js_data.get('relationships', []):
                    if rel not in data['relationships']:
                        data['relationships'].append(rel)
        
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
        if 'relationships' in data:
            for rel in data.get('relationships', []):
                source = rel.get('source')
                target = rel.get('target')
                rel_type = rel.get('type', 'association')
                label = rel.get('label', 'relates to')
                
                if source and target:
                    # Check if both source and target are in the filtered set of classes
                    if source in [c['name'] for c in classes] and target in [c['name'] for c in classes]:
                        if rel_type == 'composition':
                            relationships.append(f"  {source} *-- {target} : {label}")
                        elif rel_type == 'aggregation':
                            relationships.append(f"  {source} o-- {target} : {label}")
                        elif rel_type == 'dependency' or rel_type == 'association':
                            relationships.append(f"  {source} --> {target} : {label}")
                        elif rel_type == 'implementation':
                            relationships.append(f"  {target} <|.. {source} : {label}")
                        elif rel_type == 'inheritance':
                            relationships.append(f"  {target} <|-- {source} : {label}")
                        elif rel_type == 'trait_usage':
                            relationships.append(f"  {target} <.. {source} : {label}")
                        else:  # default to association
                            relationships.append(f"  {source} -- {target} : {label}")
        
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
                              include_external: bool = False,
                              max_modules: int = 30,
                              styles: bool = True) -> str:
        """
        Generate a Mermaid module/package diagram from parsed data.
        
        Args:
            parsed_data: Dictionary containing parsed code data
            group_by_package: Whether to group modules by package
            include_external: Whether to include external dependencies
            max_modules: Maximum number of modules to include
            styles: Whether to add styles to the diagram
            
        Returns:
            Mermaid diagram syntax as string
        """
        # Handle case where modules aren't explicitly in the data
        # but we can derive them from file paths
        modules = parsed_data.get('modules', [])
        
        # If no modules but we have classes and functions, derive modules from file paths
        if not modules and ('classes' in parsed_data or 'functions' in parsed_data):
            file_paths = set()
            
            # Get file paths from classes
            for cls in parsed_data.get('classes', []):
                if 'file_path' in cls:
                    file_paths.add(cls['file_path'])
            
            # Get file paths from functions
            for func in parsed_data.get('functions', []):
                if 'file_path' in func:
                    file_paths.add(func['file_path'])
            
            # Create module objects from file paths
            modules = []
            for file_path in file_paths:
                # Skip non-module files
                if not any(file_path.endswith(ext) for ext in ['.py', '.php', '.js', '.jsx', '.ts', '.tsx']):
                    continue
                    
                # Create a simple module representation
                relative_path = os.path.relpath(file_path, start=os.path.commonpath(list(file_paths)))
                module_name = os.path.splitext(relative_path)[0].replace('/', '.').replace('\\', '.')
                
                modules.append({
                    'name': module_name,
                    'file_path': file_path
                })
        
        if not modules:
            return "```mermaid\ngraph TD\n  NoModules[No modules found]\n```"
        
        # Limit the number of modules to avoid overly complex diagrams
        if len(modules) > max_modules:
            self.logger.warning(
                f"Module diagram has {len(modules)} modules, which exceeds the maximum "
                f"of {max_modules}. Limiting to top {max_modules} modules."
            )
            modules = modules[:max_modules]
        
        # Start building the diagram
        diagram = ["```mermaid", "graph TD"]
        
        # Add styles if requested
        if styles:
            diagram.append("  %% Styles")
            diagram.append("  classDef python fill:#3572A5,stroke:#2B5B84,color:white;")
            diagram.append("  classDef php fill:#4F5D95,stroke:#3F4A77,color:white;")
            diagram.append("  classDef javascript fill:#F7DF1E,stroke:#C6B318,color:black;")
            diagram.append("  classDef typescript fill:#007ACC,stroke:#005F9E,color:white;")
            diagram.append("  classDef package fill:#EAEAEA,stroke:#CCCCCC,color:black;")
            diagram.append("  classDef external fill:#F8F8F8,stroke:#DDDDDD,color:#888888,stroke-dasharray: 5 5;")
            diagram.append("")
        
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
                    
                    # Add style class based on file extension
                    if styles:
                        file_path = module.get('file_path', '')
                        if file_path.endswith('.py'):
                            diagram.append(f"    class {module_id} python;")
                        elif file_path.endswith('.php'):
                            diagram.append(f"    class {module_id} php;")
                        elif file_path.endswith(('.js', '.jsx')):
                            diagram.append(f"    class {module_id} javascript;")
                        elif file_path.endswith(('.ts', '.tsx')):
                            diagram.append(f"    class {module_id} typescript;")
                
                diagram.append("  end")
                
                # Add style for the package
                if styles:
                    diagram.append(f"  class {package} package;")
            
        else:
            # Add all modules as nodes
            for module in modules:
                module_id = self._clean_id(module.get('name', ''))
                module_name = module.get('name', '')
                diagram.append(f"  {module_id}[{module_name}]")
                
                # Add style class based on file extension
                if styles:
                    file_path = module.get('file_path', '')
                    if file_path.endswith('.py'):
                        diagram.append(f"  class {module_id} python;")
                    elif file_path.endswith('.php'):
                        diagram.append(f"  class {module_id} php;")
                    elif file_path.endswith(('.js', '.jsx')):
                        diagram.append(f"  class {module_id} javascript;")
                    elif file_path.endswith(('.ts', '.tsx')):
                        diagram.append(f"  class {module_id} typescript;")
        
        # Build a set of module IDs for quick lookup
        module_ids = {self._clean_id(module.get('name', '')) for module in modules}
        
        # Add dependencies between modules
        if 'dependencies' in parsed_data:
            for dep in parsed_data.get('dependencies', []):
                source = dep.get('source')
                target = dep.get('target')
                
                # Get dependency type
                dep_type = dep.get('type', 'import')
                
                # Skip external dependencies if not included
                is_source_external = self._is_external(source)
                is_target_external = self._is_external(target)
                
                if not include_external and (is_source_external or is_target_external):
                    continue
                
                source_id = self._clean_id(source)
                target_id = self._clean_id(target)
                
                # Check if source and target are in our set of modules
                source_exists = source_id in module_ids or (include_external and is_source_external)
                target_exists = target_id in module_ids or (include_external and is_target_external)
                
                if not source_exists or not target_exists:
                    continue
                
                # Add the dependency
                arrow_style = "-->"
                if dep_type == 'inherit':
                    arrow_style = "-.->|extends|"
                elif dep_type == 'import':
                    arrow_style = "-->|imports|"
                elif dep_type == 'uses':
                    arrow_style = "-->|uses|"
                
                diagram.append(f"  {source_id} {arrow_style} {target_id}")
                
                # Add style for external dependencies
                if styles:
                    if is_source_external:
                        diagram.append(f"  class {source_id} external;")
                    if is_target_external:
                        diagram.append(f"  class {target_id} external;")
        
        # Add file dependencies if available and no explicit dependencies
        elif 'file_dependencies' in parsed_data:
            file_deps = parsed_data.get('file_dependencies', {})
            
            for source_file, target_files in file_deps.items():
                source_id = self._clean_id(source_file)
                
                for target_file in target_files:
                    target_id = self._clean_id(target_file)
                    
                    # Add the dependency
                    diagram.append(f"  {source_id} -->|imports| {target_id}")
        
        # Close diagram
        diagram.append("```")
        
        return "\n".join(diagram)
    
    def generate_sequence_diagram(self, parsed_data: Dict[str, Any],
                                flow_name: str,
                                max_depth: int = 5,
                                analyze_flows: bool = True) -> str:
        """
        Generate a Mermaid sequence diagram for a specific flow.
        
        Args:
            parsed_data: Dictionary containing parsed code data
            flow_name: Name of the flow to diagram
            max_depth: Maximum depth of calls to include
            analyze_flows: Whether to automatically analyze flows if they don't exist
            
        Returns:
            Mermaid diagram syntax as string
        """
        # Make a copy of parsed_data to avoid modifying it
        data = {key: value for key, value in parsed_data.items()}
        
        # Analyze flows if they don't exist and analysis is enabled
        if analyze_flows and 'flows' not in data:
            # Determine which analyzer to use based on the files
            python_classes = [cls for cls in data.get('classes', []) 
                           if cls.get('file_path', '').endswith('.py')]
            
            if python_classes:
                # Use Python-specific flow analyzer for Python code
                python_data = {key: value for key, value in data.items()}
                python_data['classes'] = python_classes
                python_data = self.python_flow_analyzer.analyze(python_data)
                
                # Merge flows back
                if 'flows' not in data:
                    data['flows'] = {}
                
                for flow_key, flow_value in python_data.get('flows', {}).items():
                    data['flows'][flow_key] = flow_value
            
            # Use generic flow analyzer for all classes as a fallback
            if 'flows' not in data or not data['flows']:
                data = self.generic_flow_analyzer.analyze(data)
        
        flows = data.get('flows', {})
        
        # Handle special case for generating a diagram for all flows
        if flow_name == 'all' and flows:
            # Choose the first flow or a meaningful one
            # Prioritize flows with more steps
            best_flow = None
            max_steps = 0
            
            for flow_key, flow_value in flows.items():
                steps = flow_value.get('steps', [])
                if len(steps) > max_steps:
                    max_steps = len(steps)
                    best_flow = flow_key
            
            if best_flow:
                flow_name = best_flow
        
        flow = flows.get(flow_name)
        
        if not flow:
            return f"```mermaid\nsequenceDiagram\n  Note over System: Flow '{flow_name}' not found\n```"
        
        # Start building the diagram
        diagram = ["```mermaid", "sequenceDiagram"]
        
        # Add title if we have a description
        if flow.get('description'):
            diagram.append(f"  title {flow.get('description')}")
        
        # Add participants
        participants = flow.get('participants', [])
        
        # Ensure User is first if present
        if 'User' in participants:
            participants.remove('User')
            participants = ['User'] + participants
        
        for participant in participants:
            # Make participant names safe for Mermaid
            safe_name = participant.replace(' ', '_').replace('-', '_')
            label = participant
            
            # Use actor for User
            if participant == 'User':
                diagram.append(f"  actor {safe_name} as \"{label}\"")
            else:
                diagram.append(f"  participant {safe_name} as \"{label}\"")
        
        # Add sequence steps
        steps = flow.get('steps', [])
        active_participants = set()  # Track which participants are active
        
        for i, step in enumerate(steps):
            source = step.get('source', 'User')
            target = step.get('target', 'System')
            message = step.get('message', '')
            
            # Make source and target names safe for Mermaid
            source_safe = source.replace(' ', '_').replace('-', '_')
            target_safe = target.replace(' ', '_').replace('-', '_')
            
            # Track activation
            if i < len(steps) - 1 and steps[i+1].get('source') == target:
                # This target will become a source in the next step
                active_participants.add(target)
                activation = '+'
            else:
                activation = ''
            
            diagram.append(f"  {source_safe}->>+{target_safe}: {message}")
            
            # Add response if available
            response = step.get('response')
            if response:
                diagram.append(f"  {target_safe}-->>-{source_safe}: {response}")
                active_participants.discard(target)
            
            # Add deactivation for last step of each participant
            # if it doesn't have a response and is the last occurrence
            remaining_steps = steps[i+1:] if i < len(steps) - 1 else []
            target_appears_again = any(s.get('source') == target or s.get('target') == target 
                                    for s in remaining_steps)
            
            if not target_appears_again and not response and target in active_participants:
                diagram.append(f"  deactivate {target_safe}")
                active_participants.discard(target)
        
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