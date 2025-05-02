"""
Code Parser Module
-----------------
Responsible for parsing and analyzing source code from various languages,
starting with Python support.
"""

import os
import ast
import glob
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass


@dataclass
class CodeClass:
    """Class representation from parsed code."""
    name: str
    docstring: Optional[str]
    methods: List['CodeMethod']
    file_path: str
    line_number: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'docstring': self.docstring,
            'methods': [method.to_dict() for method in self.methods],
            'file_path': self.file_path,
            'line_number': self.line_number
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'docstring': self.docstring,
            'parameters': self.parameters,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'class_name': self.class_name
        }


class PythonAstParser:
    """Parser for Python files using AST."""
    
    def __init__(self, file_path: str):
        """Initialize with a Python file path."""
        self.file_path = file_path
        self.classes: List[CodeClass] = []
        self.functions: List[CodeMethod] = []
    
    def parse(self) -> Tuple[List[CodeClass], List[CodeMethod]]:
        """Parse the Python file and extract classes and functions."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            tree = ast.parse(content, filename=self.file_path)
            
            # Extract classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._process_class(node)
                elif isinstance(node, ast.FunctionDef) and node.parent_node is None:
                    # Only process top-level functions
                    self._process_function(node)
            
            return self.classes, self.functions
        
        except Exception as e:
            print(f"Error parsing {self.file_path}: {str(e)}")
            return [], []
    
    def _process_class(self, node: ast.ClassDef) -> None:
        """Process a class node from the AST."""
        methods = []
        
        # Extract methods from the class
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method = self._process_method(item, node.name)
                methods.append(method)
        
        # Create the class
        docstring = ast.get_docstring(node)
        code_class = CodeClass(
            name=node.name,
            docstring=docstring,
            methods=methods,
            file_path=self.file_path,
            line_number=node.lineno
        )
        
        self.classes.append(code_class)
    
    def _process_function(self, node: ast.FunctionDef) -> None:
        """Process a function node from the AST."""
        # Get parameters
        parameters = [arg.arg for arg in node.args.args]
        
        # Create the function
        docstring = ast.get_docstring(node)
        code_method = CodeMethod(
            name=node.name,
            docstring=docstring,
            parameters=parameters,
            file_path=self.file_path,
            line_number=node.lineno
        )
        
        self.functions.append(code_method)
    
    def _process_method(self, node: ast.FunctionDef, class_name: str) -> CodeMethod:
        """Process a method node from the AST."""
        # Get parameters
        parameters = [arg.arg for arg in node.args.args]
        if parameters and parameters[0] == 'self':
            parameters = parameters[1:]
        
        # Create the method
        docstring = ast.get_docstring(node)
        return CodeMethod(
            name=node.name,
            docstring=docstring,
            parameters=parameters,
            file_path=self.file_path,
            line_number=node.lineno,
            class_name=class_name
        )


class CodeParser:
    """Main code parser that supports multiple languages."""
    
    def __init__(self, project_path: str):
        """Initialize with a project path."""
        self.project_path = project_path
        self.classes: List[CodeClass] = []
        self.functions: List[CodeMethod] = []
    
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
        
        # TODO: Add support for other languages
        
        return {
            'classes': [cls.to_dict() for cls in self.classes],
            'functions': [func.to_dict() for func in self.functions]
        }
    
    def _find_files(self, pattern: str) -> List[str]:
        """Find files matching the pattern."""
        return glob.glob(
            os.path.join(self.project_path, pattern),
            recursive=True
        )