"""
Documentation Generator Module
-----------------------------
Generates Markdown documentation from parsed code.
"""

import os
from typing import Dict, Any, List, Optional


class DocGenerator:
    """Generates Markdown documentation from parsed code."""
    
    def __init__(self, output_dir: str):
        """Initialize with output directory."""
        self.output_dir = output_dir
    
    def generate(self, parsed_data: Dict[str, Any]) -> None:
        """Generate documentation from parsed data."""
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Generate overview
        self._generate_overview(parsed_data)
        
        # Generate class documentation
        if 'classes' in parsed_data:
            self._generate_class_docs(parsed_data['classes'])
        
        # Generate function documentation
        if 'functions' in parsed_data:
            self._generate_function_docs(parsed_data['functions'])
    
    def _generate_overview(self, parsed_data: Dict[str, Any]) -> None:
        """Generate an overview document."""
        overview_path = os.path.join(self.output_dir, "overview.md")
        
        num_classes = len(parsed_data.get('classes', []))
        num_functions = len(parsed_data.get('functions', []))
        
        with open(overview_path, 'w', encoding='utf-8') as f:
            f.write("# Project Overview\n\n")
            f.write("## Summary\n\n")
            f.write(f"- **Classes**: {num_classes}\n")
            f.write(f"- **Functions**: {num_functions}\n\n")
            
            # Add more summary information as needed
            
            # Add class listing
            if num_classes > 0:
                f.write("## Classes\n\n")
                for cls in parsed_data.get('classes', []):
                    f.write(f"- [{cls['name']}](classes/{cls['name']}.md)\n")
            
            # Add function listing
            if num_functions > 0:
                f.write("\n## Functions\n\n")
                for func in parsed_data.get('functions', []):
                    f.write(f"- [{func['name']}](functions/{func['name']}.md)\n")
    
    def _generate_class_docs(self, classes: List[Dict[str, Any]]) -> None:
        """Generate documentation for classes."""
        # Create classes directory
        classes_dir = os.path.join(self.output_dir, "classes")
        os.makedirs(classes_dir, exist_ok=True)
        
        for cls in classes:
            class_path = os.path.join(classes_dir, f"{cls['name']}.md")
            
            with open(class_path, 'w', encoding='utf-8') as f:
                f.write(f"# Class: {cls['name']}\n\n")
                
                # Add docstring
                if cls.get('docstring'):
                    f.write("## Description\n\n")
                    f.write(f"{cls['docstring']}\n\n")
                
                # Add file information
                f.write("## Source\n\n")
                f.write(f"- **File**: `{cls['file_path']}`\n")
                f.write(f"- **Line**: {cls['line_number']}\n\n")
                
                # Add methods
                if cls.get('methods'):
                    f.write("## Methods\n\n")
                    for method in cls['methods']:
                        params = ", ".join(method.get('parameters', []))
                        f.write(f"### `{method['name']}({params})`\n\n")
                        
                        if method.get('docstring'):
                            f.write(f"{method['docstring']}\n\n")
                        
                        f.write(f"- **Line**: {method['line_number']}\n\n")
    
    def _generate_function_docs(self, functions: List[Dict[str, Any]]) -> None:
        """Generate documentation for functions."""
        # Create functions directory
        functions_dir = os.path.join(self.output_dir, "functions")
        os.makedirs(functions_dir, exist_ok=True)
        
        for func in functions:
            function_path = os.path.join(functions_dir, f"{func['name']}.md")
            
            with open(function_path, 'w', encoding='utf-8') as f:
                params = ", ".join(func.get('parameters', []))
                f.write(f"# Function: `{func['name']}({params})`\n\n")
                
                # Add docstring
                if func.get('docstring'):
                    f.write("## Description\n\n")
                    f.write(f"{func['docstring']}\n\n")
                
                # Add file information
                f.write("## Source\n\n")
                f.write(f"- **File**: `{func['file_path']}`\n")
                f.write(f"- **Line**: {func['line_number']}\n")