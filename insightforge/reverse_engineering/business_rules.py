"""
Business Rules Extractor Module
------------------------------
Extracts business rules from code and documentation.
"""

import re
import ast
import os
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field


@dataclass
class BusinessRule:
    """Represents a business rule extracted from code."""
    id: str
    name: str
    description: str
    file_path: str
    line_number: int
    type: str = "validation"  # validation, calculation, process, constraint, derivation
    severity: str = "medium"  # critical, high, medium, low
    source: str = "code"  # code, comment, docstring, inferred
    code_component: Optional[str] = None  # class or method name
    related_rules: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'type': self.type,
            'severity': self.severity,
            'source': self.source,
            'code_component': self.code_component,
            'related_rules': self.related_rules
        }
    
    def to_markdown(self) -> str:
        """
        Generate Markdown representation of the business rule.
        
        Note: This method is kept for backward compatibility.
        The template system should be used for new code.
        """
        # Import here to avoid circular imports
        try:
            from .template_system import TemplateLoader
            
            # Create a temporary template loader and render the template
            loader = TemplateLoader()
            if loader.template_exists("businessrule.md.j2"):
                # Use the template system if available
                return loader.render_template("businessrule.md.j2", {"rule": self.to_dict()})
        except (ImportError, ValueError):
            # Fall back to manual generation if template system is not available
            pass
            
        # Legacy markdown generation
        result = f"# Business Rule: {self.id} - {self.name}\n\n"
        result += f"## Description\n\n{self.description}\n\n"
        result += f"## Metadata\n\n"
        result += f"- **Type**: {self.type}\n"
        result += f"- **Severity**: {self.severity}\n"
        result += f"- **Source**: {self.source}\n"
        if self.code_component:
            result += f"- **Component**: {self.code_component}\n"
        
        result += f"\n## Implementation\n\n"
        result += f"- **File**: `{self.file_path}`\n"
        result += f"- **Line**: {self.line_number}\n"
        
        if self.related_rules:
            result += f"\n## Related Rules\n\n"
            for rule_id in self.related_rules:
                result += f"- {rule_id}\n"
        
        return result


class BusinessRulesExtractor:
    """Extracts business rules from source code and documentation."""
    
    def __init__(self):
        """Initialize the business rules extractor."""
        self.rules: List[BusinessRule] = []
        self.next_id = 1
        self.rule_patterns = [
            # Explicit business rule in docstring/comment
            r"(?:Business Rule|BR)[:\s]+(.+?)(?:\n|$)",
            # Rule with ID
            r"BR-\d+[:\s]+(.+?)(?:\n|$)",
            # Constraint language
            r"(?:must|should|required to|needs to|cannot|must not)[^.\n]*(.+?)(?:\n|\.)",
            # Complete sentence with system
            r"The system (?:must|should|cannot|must not)[^.\n]*(.+?)(?:\n|\.)",
        ]
    
    def extract_from_parsed_data(self, parsed_data: Dict[str, Any]) -> List[BusinessRule]:
        """Extract business rules from parsed code data."""
        # Clear previous rules
        self.rules = []
        self.next_id = 1
        
        # Extract from classes
        for cls in parsed_data.get('classes', []):
            self._process_class(cls)
        
        # Extract from functions
        for func in parsed_data.get('functions', []):
            self._process_function(func)
        
        return self.rules
    
    def _process_class(self, cls: Dict[str, Any]) -> None:
        """Process a class to extract business rules."""
        # Extract from class docstring
        if cls.get('docstring'):
            self._extract_from_docstring(
                cls['docstring'], 
                cls['file_path'], 
                cls['line_number'],
                cls['name']
            )
        
        # Extract from methods
        for method in cls.get('methods', []):
            self._process_method(method, cls['name'])
    
    def _process_function(self, func: Dict[str, Any]) -> None:
        """Process a function to extract business rules."""
        # Extract from function docstring
        if func.get('docstring'):
            self._extract_from_docstring(
                func['docstring'], 
                func['file_path'], 
                func['line_number'],
                func['name']
            )
    
    def _process_method(self, method: Dict[str, Any], class_name: str) -> None:
        """Process a method to extract business rules."""
        # Extract from method docstring
        if method.get('docstring'):
            component = f"{class_name}.{method['name']}"
            self._extract_from_docstring(
                method['docstring'], 
                method['file_path'], 
                method['line_number'],
                component
            )
    
    def _extract_from_docstring(self, docstring: str, file_path: str, 
                              line_number: int, component: str) -> None:
        """Extract business rules from docstring."""
        # Look for explicit business rules
        for pattern in self.rule_patterns:
            matches = re.finditer(pattern, docstring, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Get the full matched text if no group
                if match.lastindex is None:
                    continue
                
                # Get the rule description (might be in different groups depending on pattern)
                if pattern.startswith(r"(?:must|should|required"):
                    # For constraint patterns, include the constraint word in the rule
                    constraint_start = match.start(0)
                    constraint_end = match.end(match.lastindex)
                    rule_text = docstring[constraint_start:constraint_end].strip()
                elif pattern.startswith(r"The system"):
                    # For "The system must" patterns, include the full phrase
                    system_start = match.start(0)
                    system_end = match.end(match.lastindex)
                    rule_text = docstring[system_start:system_end].strip()
                else:
                    # For explicit BR patterns, just use the matched group
                    rule_text = match.group(match.lastindex).strip()
                
                # Skip if too short
                if len(rule_text) < 5:
                    continue
                
                # Generate rule
                rule = self._create_rule(
                    name=self._generate_name(rule_text),
                    description=rule_text,
                    file_path=file_path,
                    line_number=line_number,
                    source="docstring",
                    code_component=component
                )
                self.rules.append(rule)
                
        # Check for PHPDoc @business-rule annotations
        php_rules_pattern = r'@(business-rule|BR)\s+(.+?)(?:\n|$)'
        for match in re.finditer(php_rules_pattern, docstring, re.IGNORECASE | re.DOTALL):
            rule_text = match.group(2).strip()
            
            # Skip if too short
            if len(rule_text) < 5:
                continue
            
            # Generate rule
            rule = self._create_rule(
                name=self._generate_name(rule_text),
                description=rule_text,
                file_path=file_path,
                line_number=line_number,
                source="phpdoc",
                code_component=component
            )
            self.rules.append(rule)
    
    def extract_from_file(self, file_path: str) -> List[BusinessRule]:
        """Extract business rules directly from a source file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Handle different file types
            if file_path.endswith('.py'):
                # Python files - use AST
                tree = ast.parse(content, filename=file_path)
                
                # Extract rules from code
                visitor = BusinessRuleVisitor(file_path)
                visitor.visit(tree)
                
                # Create rules from the visitor's findings
                for rule_info in visitor.rules:
                    rule = self._create_rule(
                        name=self._generate_name(rule_info['description']),
                        description=rule_info['description'],
                        file_path=file_path,
                        line_number=rule_info['line_number'],
                        source=rule_info['source'],
                        code_component=rule_info['component'],
                        rule_type=rule_info.get('type', 'validation')
                    )
                    self.rules.append(rule)
            
            elif file_path.endswith('.php'):
                # PHP files - use regex patterns directly
                self._extract_from_php_file(file_path, content)
            
            else:
                # For other file types, just search for patterns in the content
                self._extract_from_generic_content(file_path, content)
            
            return self.rules
            
        except Exception as e:
            print(f"Error extracting business rules from {file_path}: {str(e)}")
            return []
            
    def _extract_from_php_file(self, file_path: str, content: str) -> None:
        """Extract business rules from a PHP file."""
        # Extract docblock comments (/** ... */)
        docblock_pattern = r'/\*\*(.*?)\*/'
        docblocks = re.finditer(docblock_pattern, content, re.DOTALL)
        
        # Track current class and method
        current_class = None
        current_method = None
        
        # Simple PHP class/method detection (for context)
        class_pattern = r'class\s+(\w+)'
        method_pattern = r'function\s+(\w+)'
        
        # Line number tracking
        line_number_map = {}
        lines = content.split('\n')
        for i, line in enumerate(lines):
            for match in re.finditer(docblock_pattern, line, re.DOTALL):
                line_number_map[match.start()] = i + 1
            
            # Track classes
            class_match = re.search(class_pattern, line)
            if class_match:
                current_class = class_match.group(1)
                
            # Track methods
            method_match = re.search(method_pattern, line)
            if method_match:
                current_method = method_match.group(1)
        
        # Process each docblock
        for match in docblocks:
            docblock = match.group(1)
            
            # Get line number (approximate)
            pos = match.start()
            line_number = 1
            for pos_key in sorted(line_number_map.keys()):
                if pos >= pos_key:
                    line_number = line_number_map[pos_key]
            
            # Determine component
            component = None
            if current_class and current_method:
                component = f"{current_class}.{current_method}"
            elif current_class:
                component = current_class
            elif current_method:
                component = current_method
            
            # Extract rules from docblock
            self._extract_from_docstring(docblock, file_path, line_number, component)
            
        # Look for validation in code (if statements with exceptions)
        validation_pattern = r'if\s*\((.*?)\)\s*{\s*throw\s+new\s+(\w+)\(([^)]*)\)'
        for match in re.finditer(validation_pattern, content, re.DOTALL):
            condition = match.group(1).strip()
            exception_type = match.group(2).strip()
            exception_msg = match.group(3).strip()
            
            # Clean up exception message
            if exception_msg.startswith('"') and exception_msg.endswith('"'):
                exception_msg = exception_msg[1:-1]
            elif exception_msg.startswith("'") and exception_msg.endswith("'"):
                exception_msg = exception_msg[1:-1]
            
            # Get line number (approximate)
            pos = match.start()
            line_number = 1
            for i, line in enumerate(lines):
                if pos <= len('\n'.join(lines[:i+1])):
                    line_number = i + 1
                    break
            
            # Determine component
            component = None
            for i in range(line_number, 0, -1):
                if i-1 < len(lines):
                    method_match = re.search(r'function\s+(\w+)', lines[i-1])
                    if method_match:
                        current_method = method_match.group(1)
                        break
            
            if current_class and current_method:
                component = f"{current_class}.{current_method}"
            elif current_class:
                component = current_class
            elif current_method:
                component = current_method
            
            # Create a rule
            rule = self._create_rule(
                name=self._generate_name(exception_msg),
                description=exception_msg,
                file_path=file_path,
                line_number=line_number,
                source="code",
                code_component=component,
                rule_type="validation"
            )
            self.rules.append(rule)
    
    def _extract_from_generic_content(self, file_path: str, content: str) -> None:
        """Extract business rules from generic file content using regex."""
        # Look for explicit business rules
        for pattern in self.rule_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Get the rule description
                if match.lastindex is None:
                    continue
                
                rule_text = match.group(match.lastindex).strip()
                
                # Get approximate line number
                lines = content.split('\n')
                pos = match.start()
                line_number = 1
                for i, line in enumerate(lines):
                    if pos <= len('\n'.join(lines[:i+1])):
                        line_number = i + 1
                        break
                
                # Create a rule
                rule = self._create_rule(
                    name=self._generate_name(rule_text),
                    description=rule_text,
                    file_path=file_path,
                    line_number=line_number,
                    source="comment",
                    code_component=None
                )
                self.rules.append(rule)
    
    def _create_rule(self, name: str, description: str, file_path: str, 
                   line_number: int, source: str = "code", code_component: Optional[str] = None,
                   rule_type: str = "validation") -> BusinessRule:
        """Create a new business rule with a unique ID."""
        rule_id = f"BR-{self.next_id:03d}"
        self.next_id += 1
        
        return BusinessRule(
            id=rule_id,
            name=name,
            description=description,
            file_path=file_path,
            line_number=line_number,
            type=rule_type,
            source=source,
            code_component=code_component
        )
    
    def _generate_name(self, description: str) -> str:
        """Generate a concise name from a description."""
        # Limit to first 50 chars and capitalize
        name = description[:50]
        if len(description) > 50:
            name += "..."
        
        # Capitalize first letter if not already
        if name and not name[0].isupper():
            name = name[0].upper() + name[1:]
        
        return name


class BusinessRuleVisitor(ast.NodeVisitor):
    """AST visitor to find business rules in code."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.rules: List[Dict[str, Any]] = []
        self.current_class: Optional[str] = None
        self.current_function: Optional[str] = None
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition."""
        previous_class = self.current_class
        self.current_class = node.name
        
        # Extract docstring for business rules
        docstring = ast.get_docstring(node)
        if docstring:
            self._extract_from_docstring(docstring, node.lineno, self.current_class)
        
        # Visit children
        self.generic_visit(node)
        
        self.current_class = previous_class
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition."""
        previous_function = self.current_function
        self.current_function = node.name
        
        component = node.name
        if self.current_class:
            component = f"{self.current_class}.{node.name}"
        
        # Extract docstring for business rules
        docstring = ast.get_docstring(node)
        if docstring:
            self._extract_from_docstring(docstring, node.lineno, component)
        
        # Check for validations in function
        self._check_validations(node, component)
        
        # Visit children
        self.generic_visit(node)
        
        self.current_function = previous_function
    
    def visit_If(self, node: ast.If) -> None:
        """Visit an if statement to find validations."""
        component = self.current_function
        if self.current_class and self.current_function:
            component = f"{self.current_class}.{self.current_function}"
        
        # Check for validation patterns
        self._check_if_validation(node, component)
        
        # Visit children
        self.generic_visit(node)
    
    def visit_Assert(self, node: ast.Assert) -> None:
        """Visit an assert statement to find validations."""
        component = self.current_function
        if self.current_class and self.current_function:
            component = f"{self.current_class}.{self.current_function}"
        
        # Get the message if available
        msg = ""
        if node.msg and isinstance(node.msg, ast.Constant) and isinstance(node.msg.value, str):
            msg = node.msg.value
        
        if msg:
            self.rules.append({
                'description': msg,
                'line_number': node.lineno,
                'source': 'code',
                'component': component,
                'type': 'validation'
            })
        
        # Visit children
        self.generic_visit(node)
    
    def _extract_from_docstring(self, docstring: str, line_number: int, component: str) -> None:
        """Extract business rules from a docstring."""
        # Look for explicit business rules
        patterns = [
            r"(?:Business Rule|BR)[:\s]+(.+?)(?:\n|$)",
            r"BR-\d+[:\s]+(.+?)(?:\n|$)",
            r"(?:must|should|required to|needs to|cannot|must not)[^.\n]*(.+?)(?:\n|\.)",
            r"The system (?:must|should|cannot|must not)[^.\n]*(.+?)(?:\n|\.)",
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, docstring, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Handle different patterns
                if pattern.startswith(r"(?:must|should|required"):
                    # Get the full text for constraint patterns
                    constraint_start = match.start(0)
                    constraint_end = match.end(0)
                    rule_text = docstring[constraint_start:constraint_end].strip()
                    if rule_text.endswith('.'):
                        rule_text = rule_text[:-1]
                elif pattern.startswith(r"The system"):
                    # Get the full text for "The system must" patterns
                    system_start = match.start(0)
                    system_end = match.end(0)
                    rule_text = docstring[system_start:system_end].strip()
                    if rule_text.endswith('.'):
                        rule_text = rule_text[:-1]
                else:
                    # For explicit BR patterns, just use the matched group
                    rule_text = match.group(1).strip()
                
                # Skip if too short
                if len(rule_text) < 5:
                    continue
                
                self.rules.append({
                    'description': rule_text,
                    'line_number': line_number,
                    'source': 'docstring',
                    'component': component
                })
    
    def _check_validations(self, node: ast.FunctionDef, component: str) -> None:
        """Check for validations in a function body."""
        # Look for common validation patterns
        for item in node.body:
            # Check for validations with exceptions
            if isinstance(item, ast.If):
                self._check_if_validation(item, component)
    
    def _check_if_validation(self, node: ast.If, component: str) -> None:
        """Check if an if statement contains validations."""
        # Check if this is a validation (if condition followed by raising exception)
        has_raise = False
        exception_msg = ""
        
        for item in node.body:
            if isinstance(item, ast.Raise):
                has_raise = True
                # Try to extract the exception message
                if (hasattr(item, 'exc') and 
                    isinstance(item.exc, ast.Call) and 
                    hasattr(item.exc, 'args') and 
                    len(item.exc.args) > 0 and 
                    isinstance(item.exc.args[0], ast.Constant) and
                    isinstance(item.exc.args[0].value, str)):
                    exception_msg = item.exc.args[0].value
                break
        
        if has_raise and exception_msg:
            self.rules.append({
                'description': exception_msg,
                'line_number': node.lineno,
                'source': 'code',
                'component': component,
                'type': 'validation'
            })