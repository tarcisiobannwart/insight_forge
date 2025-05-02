"""
PHP Parser Module
---------------
Parses PHP code to extract classes, interfaces, traits, and functions.
"""

import os
import re
from typing import Dict, List, Any, Optional, Tuple, Set
import logging

# Try importing phply - this is optional and will be handled gracefully if it's not installed
try:
    from phply import phplex, phpparse
    from phply.phpparse import make_parser
    PHPLY_AVAILABLE = True
except ImportError:
    PHPLY_AVAILABLE = False
    print("Warning: phply module not found. PHP parsing will be disabled.")
    # Create dummy modules for typing purposes
    class phplex:
        class lexer:
            @staticmethod
            def clone():
                return None
    
    class phpparse:
        @staticmethod
        def make_parser():
            return None

from .code_parser import CodeClass, CodeMethod


class PHPClass:
    """Represents a PHP class extracted from code."""
    
    def __init__(
        self,
        name: str,
        docstring: Optional[str] = None,
        line_number: int = 0,
        file_path: str = "",
        is_interface: bool = False,
        is_trait: bool = False,
        namespace: Optional[str] = None
    ):
        """
        Initialize a PHP class.
        
        Args:
            name: Class name
            docstring: Class documentation string
            line_number: Line number where the class is defined
            file_path: Path to the file containing the class
            is_interface: Whether this is an interface
            is_trait: Whether this is a trait
            namespace: Namespace of the class
        """
        self.name = name
        self.docstring = docstring
        self.line_number = line_number
        self.file_path = file_path
        self.is_interface = is_interface
        self.is_trait = is_trait
        self.namespace = namespace
        self.methods: List[Dict[str, Any]] = []
        self.properties: List[Dict[str, Any]] = []
        self.constants: List[Dict[str, Any]] = []
        self.extends: List[str] = []
        self.implements: List[str] = []
        self.uses: List[str] = []  # For traits
    
    def add_method(
        self, 
        name: str, 
        docstring: Optional[str] = None,
        line_number: int = 0,
        parameters: List[Dict[str, Any]] = None,
        return_type: Optional[str] = None,
        visibility: str = "public",
        is_static: bool = False,
        is_abstract: bool = False
    ) -> None:
        """
        Add a method to the class.
        
        Args:
            name: Method name
            docstring: Method documentation
            line_number: Line number where the method is defined
            parameters: List of parameter information
            return_type: Return type of the method
            visibility: Method visibility (public, protected, private)
            is_static: Whether the method is static
            is_abstract: Whether the method is abstract
        """
        if parameters is None:
            parameters = []
            
        self.methods.append({
            'name': name,
            'docstring': docstring,
            'line_number': line_number,
            'parameters': parameters,
            'return_type': return_type,
            'visibility': visibility,
            'is_static': is_static,
            'is_abstract': is_abstract
        })
    
    def add_property(
        self,
        name: str,
        docstring: Optional[str] = None,
        line_number: int = 0,
        type_hint: Optional[str] = None,
        default_value: Optional[str] = None,
        visibility: str = "public",
        is_static: bool = False
    ) -> None:
        """
        Add a property to the class.
        
        Args:
            name: Property name
            docstring: Property documentation
            line_number: Line number where the property is defined
            type_hint: Type hint of the property
            default_value: Default value of the property
            visibility: Property visibility (public, protected, private)
            is_static: Whether the property is static
        """
        self.properties.append({
            'name': name,
            'docstring': docstring,
            'line_number': line_number,
            'type': type_hint,
            'default_value': default_value,
            'visibility': visibility,
            'is_static': is_static
        })
    
    def add_constant(
        self,
        name: str,
        value: str,
        line_number: int = 0
    ) -> None:
        """
        Add a constant to the class.
        
        Args:
            name: Constant name
            value: Constant value
            line_number: Line number where the constant is defined
        """
        self.constants.append({
            'name': name,
            'value': value,
            'line_number': line_number
        })
    
    def set_extends(self, extends: List[str]) -> None:
        """
        Set the classes this class extends.
        
        Args:
            extends: List of class names this class extends
        """
        self.extends = extends
    
    def set_implements(self, implements: List[str]) -> None:
        """
        Set the interfaces this class implements.
        
        Args:
            implements: List of interface names this class implements
        """
        self.implements = implements
    
    def set_uses(self, uses: List[str]) -> None:
        """
        Set the traits this class uses.
        
        Args:
            uses: List of trait names this class uses
        """
        self.uses = uses
    
    def get_full_name(self) -> str:
        """
        Get the fully qualified name of the class.
        
        Returns:
            Fully qualified class name with namespace
        """
        if self.namespace:
            return f"{self.namespace}\\{self.name}"
        return self.name
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the class
        """
        return {
            'name': self.name,
            'full_name': self.get_full_name(),
            'docstring': self.docstring,
            'line_number': self.line_number,
            'file_path': self.file_path,
            'is_interface': self.is_interface,
            'is_trait': self.is_trait,
            'namespace': self.namespace,
            'methods': self.methods,
            'properties': self.properties,
            'constants': self.constants,
            'extends': self.extends,
            'implements': self.implements,
            'uses': self.uses
        }


class PHPFunction:
    """Represents a PHP function extracted from code."""
    
    def __init__(
        self,
        name: str,
        docstring: Optional[str] = None,
        line_number: int = 0,
        file_path: str = "",
        parameters: List[Dict[str, Any]] = None,
        return_type: Optional[str] = None,
        namespace: Optional[str] = None
    ):
        """
        Initialize a PHP function.
        
        Args:
            name: Function name
            docstring: Function documentation
            line_number: Line number where the function is defined
            file_path: Path to the file containing the function
            parameters: List of parameter information
            return_type: Return type of the function
            namespace: Namespace of the function
        """
        self.name = name
        self.docstring = docstring
        self.line_number = line_number
        self.file_path = file_path
        self.parameters = parameters or []
        self.return_type = return_type
        self.namespace = namespace
    
    def get_full_name(self) -> str:
        """
        Get the fully qualified name of the function.
        
        Returns:
            Fully qualified function name with namespace
        """
        if self.namespace:
            return f"{self.namespace}\\{self.name}"
        return self.name
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the function
        """
        return {
            'name': self.name,
            'full_name': self.get_full_name(),
            'docstring': self.docstring,
            'line_number': self.line_number,
            'file_path': self.file_path,
            'parameters': self.parameters,
            'return_type': self.return_type,
            'namespace': self.namespace
        }


class PHPAstVisitor:
    """Visitor for PHP AST nodes."""
    
    def __init__(self, file_path: str, content: str):
        """
        Initialize the PHP AST visitor.
        
        Args:
            file_path: Path to the PHP file
            content: Content of the PHP file
        """
        self.file_path = file_path
        self.content = content
        self.current_namespace: Optional[str] = None
        self.classes: List[PHPClass] = []
        self.functions: List[PHPFunction] = []
        self.imports: Dict[str, str] = {}  # use statements
        self.interfaces: List[str] = []  # Interface names
        self.traits: List[str] = []  # Trait names
        self.class_dependencies: Dict[str, Set[str]] = {}  # Class to its dependencies
        self.logger = logging.getLogger(__name__)
    
    def visit(self, node: Any) -> None:
        """
        Visit a node in the PHP AST.
        
        Args:
            node: AST node to visit
        """
        node_type = node.__class__.__name__
        
        # Process the node based on its type
        if node_type == 'Namespace':
            self._visit_namespace(node)
        elif node_type == 'UseDeclaration':
            self._visit_use_declaration(node)
        elif node_type == 'Class':
            self._visit_class(node)
        elif node_type == 'Interface':
            self._visit_interface(node)
        elif node_type == 'Trait':
            self._visit_trait(node)
        elif node_type == 'Function':
            self._visit_function(node)
        
        # Visit children if the node is a container
        if hasattr(node, 'nodes') and node.nodes:
            for child in node.nodes:
                self.visit(child)
    
    def _visit_namespace(self, node: Any) -> None:
        """
        Visit a namespace node.
        
        Args:
            node: Namespace node
        """
        # Extract namespace name
        if isinstance(node.name, str):
            self.current_namespace = node.name
        elif hasattr(node.name, 'parts'):
            self.current_namespace = '\\'.join(node.name.parts)
    
    def _visit_use_declaration(self, node: Any) -> None:
        """
        Visit a use declaration node.
        
        Args:
            node: Use declaration node
        """
        for use in node.uses:
            alias = use.alias or use.name.parts[-1]
            full_name = '\\'.join(use.name.parts)
            self.imports[alias] = full_name
    
    def _get_docstring(self, node: Any) -> Optional[str]:
        """
        Extract docstring from a node.
        
        Args:
            node: AST node
            
        Returns:
            Docstring if found, None otherwise
        """
        if hasattr(node, 'doc_comment') and node.doc_comment:
            # Clean up the docstring
            doc = node.doc_comment
            # Remove comment markers
            doc = re.sub(r'^\s*\/\*+\s*', '', doc)
            doc = re.sub(r'\s*\*+\/\s*$', '', doc)
            # Remove leading asterisks on each line
            doc = re.sub(r'^\s*\*\s?', '', doc, flags=re.MULTILINE)
            return doc.strip()
        return None
    
    def _visit_class(self, node: Any) -> None:
        """
        Visit a class node.
        
        Args:
            node: Class node
        """
        docstring = self._get_docstring(node)
        
        # Create a new PHP class
        php_class = PHPClass(
            name=node.name,
            docstring=docstring,
            line_number=getattr(node, 'lineno', 0),
            file_path=self.file_path,
            namespace=self.current_namespace
        )
        
        # Get the full class name for dependency tracking
        class_full_name = php_class.get_full_name()
        self.class_dependencies[class_full_name] = set()
        
        # Set extends
        extends_list = []
        if node.extends:
            extends_name = node.extends.name
            if hasattr(extends_name, 'parts'):
                extends_name = '\\'.join(extends_name.parts)
            extends_list = [extends_name]
            php_class.set_extends(extends_list)
            
            # Add to dependencies
            self.class_dependencies[class_full_name].add(extends_name)
        
        # Set implements
        if node.implements:
            implements_list = []
            for impl in node.implements:
                impl_name = impl.name
                if hasattr(impl_name, 'parts'):
                    impl_name = '\\'.join(impl_name.parts)
                implements_list.append(impl_name)
                
                # Add to dependencies
                self.class_dependencies[class_full_name].add(impl_name)
            
            php_class.set_implements(implements_list)
        
        # Process class body
        if node.nodes:
            for child in node.nodes:
                self._visit_class_member(child, php_class)
        
        self.classes.append(php_class)
    
    def _visit_interface(self, node: Any) -> None:
        """
        Visit an interface node.
        
        Args:
            node: Interface node
        """
        docstring = self._get_docstring(node)
        
        # Create a new PHP class as interface
        php_class = PHPClass(
            name=node.name,
            docstring=docstring,
            line_number=getattr(node, 'lineno', 0),
            file_path=self.file_path,
            is_interface=True,
            namespace=self.current_namespace
        )
        
        # Set extends (interfaces can extend other interfaces)
        if node.extends:
            extends_list = []
            for ext in node.extends:
                ext_name = ext.name
                if hasattr(ext_name, 'parts'):
                    ext_name = '\\'.join(ext_name.parts)
                extends_list.append(ext_name)
            php_class.set_extends(extends_list)
        
        # Process interface body
        if node.nodes:
            for child in node.nodes:
                self._visit_class_member(child, php_class)
        
        # Add to classes collection
        self.classes.append(php_class)
        
        # Also add to interfaces list
        interface_full_name = php_class.get_full_name()
        self.interfaces.append(interface_full_name)
    
    def _visit_trait(self, node: Any) -> None:
        """
        Visit a trait node.
        
        Args:
            node: Trait node
        """
        docstring = self._get_docstring(node)
        
        # Create a new PHP class as trait
        php_class = PHPClass(
            name=node.name,
            docstring=docstring,
            line_number=getattr(node, 'lineno', 0),
            file_path=self.file_path,
            is_trait=True,
            namespace=self.current_namespace
        )
        
        # Process trait body
        if node.nodes:
            for child in node.nodes:
                self._visit_class_member(child, php_class)
        
        # Add to classes collection
        self.classes.append(php_class)
        
        # Also add to traits list
        trait_full_name = php_class.get_full_name()
        self.traits.append(trait_full_name)
    
    def _visit_class_member(self, node: Any, php_class: PHPClass) -> None:
        """
        Visit a class member node.
        
        Args:
            node: Member node
            php_class: PHP class to add the member to
        """
        node_type = node.__class__.__name__
        if node_type == 'Method':
            self._visit_method(node, php_class)
        elif node_type == 'Property':
            self._visit_property(node, php_class)
        elif node_type == 'ClassConstants':
            self._visit_class_constants(node, php_class)
        elif node_type == 'TraitUse':
            self._visit_trait_use(node, php_class)
    
    def _visit_method(self, node: Any, php_class: PHPClass) -> None:
        """
        Visit a method node.
        
        Args:
            node: Method node
            php_class: PHP class to add the method to
        """
        docstring = self._get_docstring(node)
        
        # Extract visibility
        visibility = "public"
        if node.modifiers:
            if "private" in node.modifiers:
                visibility = "private"
            elif "protected" in node.modifiers:
                visibility = "protected"
        
        # Check if static or abstract
        is_static = "static" in (node.modifiers or [])
        is_abstract = "abstract" in (node.modifiers or [])
        
        # Extract parameters
        parameters = []
        if node.params:
            for param in node.params:
                param_info = {'name': param.name}
                
                # Extract type hint if available
                type_hint = None
                if hasattr(param, 'type') and param.type:
                    if isinstance(param.type, str):
                        type_hint = param.type
                    elif hasattr(param.type, 'parts'):
                        type_hint = '\\'.join(param.type.parts)
                
                if type_hint:
                    param_info['type'] = type_hint
                
                # Extract default value if available
                if hasattr(param, 'default') and param.default:
                    value = param.default
                    if isinstance(value, str):
                        param_info['default'] = f'"{value}"'
                    elif isinstance(value, (int, float, bool)):
                        param_info['default'] = str(value)
                    else:
                        param_info['default'] = "..."
                
                parameters.append(param_info)
        
        # Extract return type
        return_type = None
        if hasattr(node, 'return_type') and node.return_type:
            if isinstance(node.return_type, str):
                return_type = node.return_type
            elif hasattr(node.return_type, 'parts'):
                return_type = '\\'.join(node.return_type.parts)
        
        # Add the method to the class
        php_class.add_method(
            name=node.name,
            docstring=docstring,
            line_number=getattr(node, 'lineno', 0),
            parameters=parameters,
            return_type=return_type,
            visibility=visibility,
            is_static=is_static,
            is_abstract=is_abstract
        )
    
    def _visit_property(self, node: Any, php_class: PHPClass) -> None:
        """
        Visit a property node.
        
        Args:
            node: Property node
            php_class: PHP class to add the property to
        """
        docstring = self._get_docstring(node)
        
        # Extract visibility
        visibility = "public"
        if node.modifiers:
            if "private" in node.modifiers:
                visibility = "private"
            elif "protected" in node.modifiers:
                visibility = "protected"
        
        # Check if static
        is_static = "static" in (node.modifiers or [])
        
        # Process each property declaration
        for prop in node.nodes:
            name = prop.name
            default_value = None
            
            # Extract default value if available
            if hasattr(prop, 'default') and prop.default:
                value = prop.default
                if isinstance(value, str):
                    default_value = f'"{value}"'
                elif isinstance(value, (int, float, bool)):
                    default_value = str(value)
                else:
                    default_value = "..."
            
            # Extract type hint from docstring or property declaration
            type_hint = None
            if hasattr(node, 'type') and node.type:
                if isinstance(node.type, str):
                    type_hint = node.type
                elif hasattr(node.type, 'parts'):
                    type_hint = '\\'.join(node.type.parts)
            
            # Add the property to the class
            php_class.add_property(
                name=name,
                docstring=docstring,
                line_number=getattr(node, 'lineno', 0),
                type_hint=type_hint,
                default_value=default_value,
                visibility=visibility,
                is_static=is_static
            )
    
    def _visit_class_constants(self, node: Any, php_class: PHPClass) -> None:
        """
        Visit a class constants node.
        
        Args:
            node: Class constants node
            php_class: PHP class to add the constants to
        """
        # Process each constant declaration
        for const in node.nodes:
            name = const.name
            value = "..."
            
            # Extract value if available
            if hasattr(const, 'value'):
                if isinstance(const.value, str):
                    value = f'"{const.value}"'
                elif isinstance(const.value, (int, float, bool)):
                    value = str(const.value)
            
            # Add the constant to the class
            php_class.add_constant(
                name=name,
                value=value,
                line_number=getattr(node, 'lineno', 0)
            )
    
    def _visit_trait_use(self, node: Any, php_class: PHPClass) -> None:
        """
        Visit a trait use node.
        
        Args:
            node: Trait use node
            php_class: PHP class to add the trait use to
        """
        # Extract trait names
        trait_list = []
        for trait in node.traits:
            trait_name = trait.name
            if hasattr(trait_name, 'parts'):
                trait_name = '\\'.join(trait_name.parts)
            trait_list.append(trait_name)
            
            # Add to class dependencies
            class_full_name = php_class.get_full_name()
            if class_full_name in self.class_dependencies:
                self.class_dependencies[class_full_name].add(trait_name)
        
        php_class.set_uses(trait_list)
    
    def _visit_function(self, node: Any) -> None:
        """
        Visit a function node.
        
        Args:
            node: Function node
        """
        # Skip methods, we handle them with _visit_method
        if hasattr(node, 'is_method') and node.is_method:
            return
        
        docstring = self._get_docstring(node)
        
        # Extract parameters
        parameters = []
        if node.params:
            for param in node.params:
                param_info = {'name': param.name}
                
                # Extract type hint if available
                type_hint = None
                if hasattr(param, 'type') and param.type:
                    if isinstance(param.type, str):
                        type_hint = param.type
                    elif hasattr(param.type, 'parts'):
                        type_hint = '\\'.join(param.type.parts)
                
                if type_hint:
                    param_info['type'] = type_hint
                
                # Extract default value if available
                if hasattr(param, 'default') and param.default:
                    value = param.default
                    if isinstance(value, str):
                        param_info['default'] = f'"{value}"'
                    elif isinstance(value, (int, float, bool)):
                        param_info['default'] = str(value)
                    else:
                        param_info['default'] = "..."
                
                parameters.append(param_info)
        
        # Extract return type
        return_type = None
        if hasattr(node, 'return_type') and node.return_type:
            if isinstance(node.return_type, str):
                return_type = node.return_type
            elif hasattr(node.return_type, 'parts'):
                return_type = '\\'.join(node.return_type.parts)
        
        # Create a new PHP function
        php_function = PHPFunction(
            name=node.name,
            docstring=docstring,
            line_number=getattr(node, 'lineno', 0),
            file_path=self.file_path,
            parameters=parameters,
            return_type=return_type,
            namespace=self.current_namespace
        )
        
        self.functions.append(php_function)


class PHPParser:
    """
    Parser for PHP files that extracts classes, interfaces, traits, and functions.
    """
    
    def __init__(self, file_path: str = None):
        """
        Initialize the PHP parser.
        
        Args:
            file_path: Path to the PHP file to parse
        """
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)
    
    def parse(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        """
        Parse the PHP file to extract classes and functions.
        
        Returns:
            Tuple of (classes, functions, metadata) as dictionaries
        """
        if not self.file_path:
            return [], [], {}
        
        # If phply is not available, return empty results
        if not PHPLY_AVAILABLE:
            self.logger.warning("phply module not available. Cannot parse PHP file.")
            return [], [], {}
            
        try:
            # Read the file
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create the parser
            lexer = phplex.lexer.clone()
            parser = make_parser()
            
            # Parse the file
            ast = parser.parse(content, lexer=lexer)
            
            # Visit AST nodes
            visitor = PHPAstVisitor(self.file_path, content)
            if ast:
                for node in ast:
                    visitor.visit(node)
            
            # Convert to dictionaries
            classes = [cls.to_dict() for cls in visitor.classes]
            functions = [func.to_dict() for func in visitor.functions]
            
            # Gather metadata
            metadata = {
                'namespaces': [visitor.current_namespace] if visitor.current_namespace else [],
                'imports': visitor.imports,
                'interfaces': visitor.interfaces,
                'traits': visitor.traits,
                'class_dependencies': {k: list(v) for k, v in visitor.class_dependencies.items()}
            }
            
            return classes, functions, metadata
            
        except Exception as e:
            self.logger.error(f"Error parsing PHP file {self.file_path}: {str(e)}")
            return [], [], {}


class PHPProjectParser:
    """Parser for PHP projects."""
    
    def __init__(
        self,
        project_dir: str,
        exclude_dirs: List[str] = None,
        file_extensions: List[str] = None
    ):
        """
        Initialize the PHP project parser.
        
        Args:
            project_dir: Root directory of the project
            exclude_dirs: Directories to exclude from parsing
            file_extensions: File extensions to include
        """
        self.project_dir = project_dir
        self.exclude_dirs = exclude_dirs or ['vendor', 'node_modules', 'tests', 'test']
        self.file_extensions = file_extensions or ['.php']
        self.logger = logging.getLogger(__name__)
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse the PHP project.
        
        Returns:
            Dictionary with parsed data
        """
        all_classes = []
        all_functions = []
        all_namespaces = set()
        all_interfaces = set()
        all_traits = set()
        class_dependencies = {}
        file_dependencies = {}
        
        # Find all PHP files
        php_files = self._find_php_files()
        
        # Parse each file
        for file_path in php_files:
            self.logger.debug(f"Parsing PHP file: {file_path}")
            
            parser = PHPParser(file_path)
            classes, functions, metadata = parser.parse()
            
            # Extract namespaces
            for namespace in metadata.get('namespaces', []):
                if namespace:
                    all_namespaces.add(namespace)
                    
            # Extract interfaces and traits
            all_interfaces.update(metadata.get('interfaces', []))
            all_traits.update(metadata.get('traits', []))
            
            # Merge class dependencies
            for class_name, deps in metadata.get('class_dependencies', {}).items():
                if class_name not in class_dependencies:
                    class_dependencies[class_name] = set()
                class_dependencies[class_name].update(deps)
            
            # Add to collections
            all_classes.extend(classes)
            all_functions.extend(functions)
            
            # Extract additional namespaces from classes and functions
            for cls in classes:
                if cls.get('namespace'):
                    all_namespaces.add(cls['namespace'])
            
            for func in functions:
                if func.get('namespace'):
                    all_namespaces.add(func['namespace'])
            
            # TODO: Extract file dependencies based on imports
            
        return {
            'classes': all_classes,
            'functions': all_functions,
            'namespaces': list(all_namespaces),
            'interfaces': list(all_interfaces),
            'traits': list(all_traits),
            'class_dependencies': {k: list(v) for k, v in class_dependencies.items()},
            'file_dependencies': file_dependencies
        }
    
    def _find_php_files(self) -> List[str]:
        """
        Find all PHP files in the project.
        
        Returns:
            List of paths to PHP files
        """
        php_files = []
        
        for root, dirs, files in os.walk(self.project_dir):
            # Remove excluded directories
            for exclude_dir in self.exclude_dirs:
                if exclude_dir in dirs:
                    dirs.remove(exclude_dir)
            
            # Add PHP files
            for file in files:
                if any(file.endswith(ext) for ext in self.file_extensions):
                    php_files.append(os.path.join(root, file))
        
        return php_files


def adapt_php_to_insightforge(parsed_php_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adapt PHP parsed data to InsightForge format.
    
    Args:
        parsed_php_data: Data parsed by PHPProjectParser
        
    Returns:
        Data in InsightForge format
    """
    insightforge_classes = []
    
    # Convert PHP classes to InsightForge format
    for php_class in parsed_php_data.get('classes', []):
        # Create methods list
        methods = []
        for method in php_class.get('methods', []):
            code_method = CodeMethod(
                name=method['name'],
                docstring=method.get('docstring', ''),
                line_number=method.get('line_number', 0),
                parameters=[p['name'] for p in method.get('parameters', [])],
                file_path=php_class.get('file_path', ''),
                class_name=php_class['name'],
                return_type=method.get('return_type')
            )
            methods.append(code_method)
        
        # Create code class
        code_class = CodeClass(
            name=php_class['name'],
            docstring=php_class.get('docstring', ''),
            methods=methods,
            line_number=php_class.get('line_number', 0),
            file_path=php_class.get('file_path', '')
        )
        
        # Add base classes
        code_class.base_classes = php_class.get('extends', [])
        code_class.base_classes.extend(php_class.get('implements', []))
        
        # Add properties as attributes
        for prop in php_class.get('properties', []):
            code_class.attributes.append({
                'name': prop['name'],
                'type': prop.get('type'),
                'is_class_var': prop.get('is_static', False),
                'line_number': prop.get('line_number', 0),
                'docstring': prop.get('docstring', ''),
                'visibility': prop.get('visibility', 'public')
            })
        
        # Add constants as attributes
        for const in php_class.get('constants', []):
            code_class.attributes.append({
                'name': const['name'],
                'type': 'const',
                'is_class_var': True,  # Constants are static
                'line_number': const.get('line_number', 0),
                'docstring': f"Constant value: {const.get('value', '')}",
                'visibility': 'public'  # Constants are public by default in PHP
            })
        
        # Add traits as metadata (InsightForge doesn't have a direct trait concept)
        if php_class.get('uses'):
            code_class.attributes.append({
                'name': '__traits__',
                'type': 'metadata',
                'is_class_var': True,
                'line_number': 0,
                'docstring': f"Traits: {', '.join(php_class.get('uses', []))}",
                'visibility': 'public'
            })
        
        # Add metadata for interface or trait
        if php_class.get('is_interface'):
            code_class.attributes.append({
                'name': '__type__',
                'type': 'metadata',
                'is_class_var': True,
                'line_number': 0,
                'docstring': 'This is a PHP interface',
                'visibility': 'public'
            })
        elif php_class.get('is_trait'):
            code_class.attributes.append({
                'name': '__type__',
                'type': 'metadata',
                'is_class_var': True,
                'line_number': 0,
                'docstring': 'This is a PHP trait',
                'visibility': 'public'
            })
        
        # Add namespace metadata
        if php_class.get('namespace'):
            code_class.attributes.append({
                'name': '__namespace__',
                'type': 'metadata',
                'is_class_var': True,
                'line_number': 0,
                'docstring': f"Namespace: {php_class.get('namespace')}",
                'visibility': 'public'
            })
        
        # Add to collection
        insightforge_classes.append(code_class.to_dict())
    
    # Convert PHP functions to InsightForge format
    insightforge_functions = []
    for php_function in parsed_php_data.get('functions', []):
        func_dict = {
            'name': php_function['name'],
            'docstring': php_function.get('docstring', ''),
            'line_number': php_function.get('line_number', 0),
            'file_path': php_function.get('file_path', ''),
            'parameters': [p['name'] for p in php_function.get('parameters', [])],
            'return_type': php_function.get('return_type')
        }
        
        # Add namespace information if available
        if php_function.get('namespace'):
            func_dict['namespace'] = php_function['namespace']
            
        insightforge_functions.append(func_dict)
    
    # Create a dependency mapping from class dependencies
    class_deps = parsed_php_data.get('class_dependencies', {})
    file_deps = parsed_php_data.get('file_dependencies', {})
    dependencies = []
    
    # Add mapped class dependencies
    for source_class, target_classes in class_deps.items():
        for target in target_classes:
            dependencies.append({
                'source': source_class,
                'target': target,
                'type': 'class_dependency'
            })
    
    # Add file dependencies
    for source_file, target_files in file_deps.items():
        for target in target_files:
            dependencies.append({
                'source': source_file,
                'target': target,
                'type': 'file_dependency'
            })
    
    # Return in InsightForge format
    return {
        'classes': insightforge_classes,
        'functions': insightforge_functions,
        'modules': [],  # PHP doesn't have modules like Python
        'dependencies': dependencies,
        'namespaces': parsed_php_data.get('namespaces', []),
        'interfaces': parsed_php_data.get('interfaces', []),
        'traits': parsed_php_data.get('traits', [])
    }