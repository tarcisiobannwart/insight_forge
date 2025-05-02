"""
Code Parser Module
-----------------
Responsible for parsing and analyzing source code from various languages,
starting with Python support.
"""

import os
import ast
import glob
import fnmatch
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field


@dataclass
class CodeClass:
    """Class representation from parsed code."""
    name: str
    docstring: Optional[str]
    methods: List['CodeMethod']
    file_path: str
    line_number: int
    base_classes: List[str] = field(default_factory=list)
    attributes: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'docstring': self.docstring,
            'methods': [method.to_dict() for method in self.methods],
            'file_path': self.file_path,
            'line_number': self.line_number,
            'base_classes': self.base_classes,
            'attributes': self.attributes
        }


@dataclass
class CodeMethod:
    """Method representation from parsed code."""
    name: str
    docstring: Optional[str]
    parameters: List[str]
    file_path: str
    line_number: int
    class_name: Optional[str] = None
    return_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'docstring': self.docstring,
            'parameters': self.parameters,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'class_name': self.class_name,
            'return_type': self.return_type
        }


class PythonAstParser:
    """Parser for Python files using AST."""
    
    def __init__(self, file_path: str):
        """Initialize with a Python file path."""
        self.file_path = file_path
        self.classes: List[CodeClass] = []
        self.functions: List[CodeMethod] = []
        self.imports: Dict[str, str] = {}  # Mapping of imported names to their modules
    
    def parse(self) -> Tuple[List[CodeClass], List[CodeMethod]]:
        """Parse the Python file and extract classes and functions."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            tree = ast.parse(content, filename=self.file_path)
            
            # Process imports first to resolve base class references
            self._process_imports(tree)
            
            # First pass to collect all top-level nodes
            top_level_classes = []
            top_level_functions = []
            
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    top_level_classes.append(node)
                elif isinstance(node, ast.FunctionDef):
                    top_level_functions.append(node)
            
            # Process classes
            for class_node in top_level_classes:
                self._process_class(class_node)
            
            # Process top-level functions
            for func_node in top_level_functions:
                self._process_function(func_node)
            
            return self.classes, self.functions
        
        except Exception as e:
            print(f"Error parsing {self.file_path}: {str(e)}")
            return [], []
    
    def _process_imports(self, tree: ast.Module) -> None:
        """Process import statements to track imported names."""
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    self.imports[name.asname or name.name] = name.name
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for name in node.names:
                    imported_name = name.asname or name.name
                    self.imports[imported_name] = f"{module}.{name.name}" if module else name.name
    
    def _get_base_class_names(self, bases: List[ast.expr]) -> List[str]:
        """Extract base class names from the class bases expressions."""
        base_names = []
        
        for base in bases:
            if isinstance(base, ast.Name):
                # Simple case: class Child(Parent)
                base_names.append(base.id)
            elif isinstance(base, ast.Attribute):
                # Module case: class Child(module.Parent)
                # Reconstruct the full name
                base_name = self._get_attribute_full_name(base)
                base_names.append(base_name)
        
        return base_names
    
    def _get_attribute_full_name(self, node: ast.Attribute) -> str:
        """Recursively build the full dotted name of an attribute."""
        if isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        elif isinstance(node.value, ast.Attribute):
            return f"{self._get_attribute_full_name(node.value)}.{node.attr}"
        return node.attr
    
    def _extract_attributes(self, class_node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Extract attributes defined in the class."""
        attributes = []
        
        # Find class-level attributes (direct assignments)
        for item in class_node.body:
            # Class attribute: class_var = value
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append({
                            'name': target.id,
                            'line_number': item.lineno,
                            'is_class_var': True
                        })
        
        # Find instance attributes (self.attr = value in __init__)
        init_method = None
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                init_method = item
                break
        
        if init_method:
            for node in ast.walk(init_method):
                # Instance attribute: self.attr = value
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                            if target.value.id == 'self':
                                attributes.append({
                                    'name': target.attr,
                                    'line_number': node.lineno,
                                    'is_class_var': False
                                })
        
        return attributes
    
    def _process_class(self, node: ast.ClassDef) -> None:
        """Process a class node from the AST."""
        methods = []
        
        # Extract methods from the class
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method = self._process_method(item, node.name)
                methods.append(method)
        
        # Extract base classes
        base_classes = self._get_base_class_names(node.bases)
        
        # Extract class attributes
        attributes = self._extract_attributes(node)
        
        # Create the class
        docstring = ast.get_docstring(node)
        code_class = CodeClass(
            name=node.name,
            docstring=docstring,
            methods=methods,
            file_path=self.file_path,
            line_number=node.lineno,
            base_classes=base_classes,
            attributes=attributes
        )
        
        self.classes.append(code_class)
    
    def _process_function(self, node: ast.FunctionDef) -> None:
        """Process a function node from the AST."""
        # Get parameters
        parameters = [arg.arg for arg in node.args.args]
        
        # Extract return type if available
        return_type = None
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return_type = node.returns.id
            elif isinstance(node.returns, ast.Attribute):
                return_type = self._get_attribute_full_name(node.returns)
        
        # Create the function
        docstring = ast.get_docstring(node)
        code_method = CodeMethod(
            name=node.name,
            docstring=docstring,
            parameters=parameters,
            file_path=self.file_path,
            line_number=node.lineno,
            return_type=return_type
        )
        
        self.functions.append(code_method)
    
    def _process_method(self, node: ast.FunctionDef, class_name: str) -> CodeMethod:
        """Process a method node from the AST."""
        # Get parameters
        parameters = [arg.arg for arg in node.args.args]
        if parameters and parameters[0] == 'self':
            parameters = parameters[1:]
        
        # Extract return type if available
        return_type = None
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return_type = node.returns.id
            elif isinstance(node.returns, ast.Attribute):
                return_type = self._get_attribute_full_name(node.returns)
        
        # Create the method
        docstring = ast.get_docstring(node)
        return CodeMethod(
            name=node.name,
            docstring=docstring,
            parameters=parameters,
            file_path=self.file_path,
            line_number=node.lineno,
            class_name=class_name,
            return_type=return_type
        )


class CodeParser:
    """Main code parser that supports multiple languages."""
    
    def __init__(self, project_path: str, exclude_dirs: List[str] = None, exclude_files: List[str] = None):
        """
        Initialize with a project path.
        
        Args:
            project_path: Path to the project directory
            exclude_dirs: List of directories to exclude from analysis
            exclude_files: List of file patterns to exclude from analysis
        """
        self.project_path = project_path
        self.classes: List[CodeClass] = []
        self.functions: List[CodeMethod] = []
        self.dependencies: Dict[str, Set[str]] = {}  # File to its dependencies
        self.exclude_dirs = exclude_dirs or []
        self.exclude_files = exclude_files or []
    
    def parse(self) -> Dict[str, Any]:
        """Parse the project for code elements."""
        # Find Python files
        python_files = self._find_files("**/*.py")
        
        # Parse Python files
        for file_path in python_files:
            parser = PythonAstParser(file_path)
            classes, functions = parser.parse()
            
            self.classes.extend(classes)
            self.functions.extend(functions)
            
            # Extract dependencies between files
            rel_path = os.path.relpath(file_path, self.project_path)
            self._process_dependencies(rel_path, parser.imports)
        
        # Find PHP files
        php_files = self._find_files("**/*.php")
        
        # Parse PHP files
        try:
            from .php_parser import PHPParser, adapt_php_to_insightforge
            
            for file_path in php_files:
                parser = PHPParser(file_path)
                classes, functions = parser.parse()
                
                if classes or functions:
                    # Convert PHP parsed data to InsightForge format
                    php_data = {
                        'classes': classes,
                        'functions': functions
                    }
                    
                    insightforge_data = adapt_php_to_insightforge(php_data)
                    
                    # Add parsed classes to our collection
                    for class_dict in insightforge_data['classes']:
                        # Convert dict back to CodeClass
                        code_class = CodeClass(
                            name=class_dict['name'],
                            docstring=class_dict['docstring'],
                            methods=[
                                CodeMethod(
                                    name=m['name'],
                                    docstring=m['docstring'],
                                    parameters=m['parameters'],
                                    file_path=class_dict['file_path'],
                                    line_number=m['line_number'],
                                    class_name=class_dict['name'],
                                    return_type=m.get('return_type')
                                ) for m in class_dict['methods']
                            ],
                            file_path=class_dict['file_path'],
                            line_number=class_dict['line_number'],
                            base_classes=class_dict['base_classes'],
                            attributes=class_dict['attributes']
                        )
                        self.classes.append(code_class)
                    
                    # Add parsed functions
                    for func_dict in insightforge_data['functions']:
                        func = CodeMethod(
                            name=func_dict['name'],
                            docstring=func_dict['docstring'],
                            parameters=func_dict['parameters'],
                            file_path=func_dict['file_path'],
                            line_number=func_dict['line_number'],
                            return_type=func_dict.get('return_type')
                        )
                        self.functions.append(func)
                
                # TODO: Extract dependencies between PHP files
        except ImportError:
            print("PHP parser not available, skipping PHP files")
        
        return {
            'classes': [cls.to_dict() for cls in self.classes],
            'functions': [func.to_dict() for func in self.functions],
            'dependencies': {src: list(deps) for src, deps in self.dependencies.items()}
        }
    
    def _process_dependencies(self, file_path: str, imports: Dict[str, str]) -> None:
        """Process file dependencies based on imports."""
        if file_path not in self.dependencies:
            self.dependencies[file_path] = set()
        
        # Handle each import
        for imported_name, module_path in imports.items():
            # Simple case: direct import from another file in the same directory
            if module_path and '.' not in module_path:
                potential_path = f"{module_path}.py"
                if os.path.exists(os.path.join(self.project_path, potential_path)):
                    self.dependencies[file_path].add(potential_path)
            
            # More complex: import from package/subpackage
            elif '.' in module_path:
                # Convert module path to potential file path
                module_parts = module_path.split('.')
                # Try different possibilities for the import path
                for i in range(len(module_parts)):
                    potential_path = os.path.join(*module_parts[:i+1]) + '.py'
                    if os.path.exists(os.path.join(self.project_path, potential_path)):
                        self.dependencies[file_path].add(potential_path)
                        break
    
    def _find_files(self, pattern: str) -> List[str]:
        """
        Find files matching the pattern, excluding specified directories and files.
        
        Args:
            pattern: Glob pattern to match files
            
        Returns:
            List of file paths matching the pattern
        """
        all_files = glob.glob(
            os.path.join(self.project_path, pattern),
            recursive=True
        )
        
        # Filter out excluded directories and files
        filtered_files = []
        for file_path in all_files:
            # Convert to relative path for easier matching
            rel_path = os.path.relpath(file_path, self.project_path)
            
            # Skip if in excluded directory
            if any(part for part in rel_path.split(os.sep) if part in self.exclude_dirs):
                continue
                
            # Skip if matches excluded file pattern
            if any(fnmatch.fnmatch(os.path.basename(file_path), pattern) for pattern in self.exclude_files):
                continue
                
            filtered_files.append(file_path)
            
        return filtered_files