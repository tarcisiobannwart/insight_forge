"""
Tests for the JavaScript/TypeScript parser.
"""

import os
import pytest
from insightforge.reverse_engineering.javascript_parser import (
    JavaScriptParser, 
    JavaScriptProjectParser, 
    JsClass, 
    JsFunction, 
    adapt_js_to_insightforge,
    check_nodejs_available,
    check_npm_available
)

# Skip all tests if Node.js is not available
nodejs_available = check_nodejs_available() and check_npm_available()
pytestmark = pytest.mark.skipif(
    not nodejs_available, 
    reason="Node.js and npm are required for JavaScript/TypeScript parsing"
)


class TestJavaScriptParser:
    """Test class for JavaScript parser."""
    
    def test_javascript_parser_initialization(self):
        """Test JavaScript parser initialization."""
        parser = JavaScriptParser()
        assert parser.file_path is None
        assert parser.is_typescript is False
        
        parser = JavaScriptParser(file_path="/path/to/file.js")
        assert parser.file_path == "/path/to/file.js"
        assert parser.is_typescript is False
        
        parser = JavaScriptParser(file_path="/path/to/file.ts")
        assert parser.file_path == "/path/to/file.ts"
        assert parser.is_typescript is True
    
    def test_javascript_parser_parse_empty_file(self, tmp_path):
        """Test parsing an empty JavaScript file."""
        # Create an empty JavaScript file
        empty_file = tmp_path / "empty.js"
        empty_file.write_text("// Empty file\n")
        
        # Parse it
        parser = JavaScriptParser(str(empty_file))
        classes, functions, metadata = parser.parse()
        
        # Check results
        assert len(classes) == 0
        assert len(functions) == 0
    
    def test_javascript_parser_parse_class(self, tmp_path):
        """Test parsing a JavaScript file with a class."""
        # Create a JS file with a simple class
        class_file = tmp_path / "class.js"
        class_file.write_text("""/**
 * Test class
 */
class TestClass {
    constructor(name) {
        this.name = name;
        this._private = 'private';
    }
    
    /**
     * Test method
     */
    test() {
        return true;
    }
}
""")
        
        # Parse it
        parser = JavaScriptParser(str(class_file))
        classes, functions, metadata = parser.parse()
        
        # Check results
        assert len(classes) == 1
        assert classes[0]['name'] == 'TestClass'
        assert len(classes[0]['methods']) == 2  # constructor and test
        assert classes[0]['methods'][0]['name'] == 'constructor'
        assert classes[0]['methods'][1]['name'] == 'test'
    
    def test_javascript_parser_parse_class_inheritance(self, tmp_path):
        """Test parsing a JavaScript file with class inheritance."""
        # Create a JS file with inheritance
        inheritance_file = tmp_path / "inheritance.js"
        inheritance_file.write_text("""class BaseClass {
    baseMethod() {
        return 'base';
    }
}

class ChildClass extends BaseClass {
    childMethod() {
        return 'child';
    }
}
""")
        
        # Parse it
        parser = JavaScriptParser(str(inheritance_file))
        classes, functions, metadata = parser.parse()
        
        # Check results
        assert len(classes) == 2
        
        # Find the ChildClass
        child_class = None
        for cls in classes:
            if cls['name'] == 'ChildClass':
                child_class = cls
                break
        
        assert child_class is not None
        assert child_class['extends'] == ['BaseClass']
    
    def test_javascript_parser_parse_function(self, tmp_path):
        """Test parsing a JavaScript file with functions."""
        # Create a JS file with functions
        function_file = tmp_path / "function.js"
        function_file.write_text("""/**
 * Test function
 */
function testFunction(param) {
    return param;
}

const arrowFunction = (a, b) => a + b;

function* generatorFunction() {
    yield 1;
    yield 2;
}
""")
        
        # Parse it
        parser = JavaScriptParser(str(function_file))
        classes, functions, metadata = parser.parse()
        
        # Check results
        assert len(classes) == 0
        assert len(functions) == 3
        
        function_names = [f['name'] for f in functions]
        assert 'testFunction' in function_names
        assert 'arrowFunction' in function_names
        assert 'generatorFunction' in function_names
        
        # Find the generator function
        generator_func = None
        for func in functions:
            if func['name'] == 'generatorFunction':
                generator_func = func
                break
        
        assert generator_func is not None
        assert generator_func['is_generator'] is True
    
    def test_typescript_parser_parse_interface(self, tmp_path):
        """Test parsing a TypeScript file with an interface."""
        # Skip if not running in TypeScript environment
        if not nodejs_available:
            pytest.skip("Node.js not available for TypeScript parsing")
        
        # Create a TS file with an interface
        interface_file = tmp_path / "interface.ts"
        interface_file.write_text("""/**
 * Test interface
 */
interface TestInterface {
    id: number;
    name: string;
    
    /**
     * Test method
     */
    test(): boolean;
}
""")
        
        # Parse it
        parser = JavaScriptParser(str(interface_file))
        classes, functions, metadata = parser.parse()
        
        # Check results
        assert len(classes) == 1
        assert classes[0]['name'] == 'TestInterface'
        assert classes[0]['is_interface'] is True
        assert len(classes[0]['methods']) == 1
        assert classes[0]['methods'][0]['name'] == 'test'
    
    def test_typescript_parser_parse_enum(self, tmp_path):
        """Test parsing a TypeScript file with an enum."""
        # Create a TS file with an enum
        enum_file = tmp_path / "enum.ts"
        enum_file.write_text("""/**
 * Test enum
 */
enum TestEnum {
    A = 'a',
    B = 'b',
    C = 'c'
}
""")
        
        # Parse it
        parser = JavaScriptParser(str(enum_file))
        classes, functions, metadata = parser.parse()
        
        # Check results
        assert len(classes) == 1
        assert classes[0]['name'] == 'TestEnum'
        assert classes[0]['is_enum'] is True


class TestJavaScriptProjectParser:
    """Test class for JavaScript project parser."""
    
    def test_javascript_project_parser_initialization(self):
        """Test JavaScript project parser initialization."""
        parser = JavaScriptProjectParser(project_dir="/path/to/project")
        assert parser.project_dir == "/path/to/project"
        assert 'node_modules' in parser.exclude_dirs
        assert '.js' in parser.file_extensions
        assert '.ts' in parser.file_extensions
    
    def test_javascript_project_parser_find_js_files(self, tmp_path):
        """Test finding JS files in a project."""
        # Create project structure
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        # Create JS files
        (project_dir / "file1.js").write_text("// JS file\n")
        (project_dir / "file2.jsx").write_text("// JSX file\n")
        
        # Create TS files
        (project_dir / "file3.ts").write_text("// TS file\n")
        (project_dir / "file4.tsx").write_text("// TSX file\n")
        
        # Create subdirectory
        sub_dir = project_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "file5.js").write_text("// JS file in subdir\n")
        
        # Create node_modules directory that should be excluded
        node_modules_dir = project_dir / "node_modules"
        node_modules_dir.mkdir()
        (node_modules_dir / "module.js").write_text("// Module\n")
        
        # Initialize parser
        parser = JavaScriptProjectParser(project_dir=str(project_dir))
        
        # Find JS files
        js_files = parser._find_js_files()
        
        # Check results
        assert len(js_files) == 5
        assert str(project_dir / "file1.js") in js_files
        assert str(project_dir / "file2.jsx") in js_files
        assert str(project_dir / "file3.ts") in js_files
        assert str(project_dir / "file4.tsx") in js_files
        assert str(sub_dir / "file5.js") in js_files
        assert str(node_modules_dir / "module.js") not in js_files
    
    def test_adapt_js_to_insightforge(self, tmp_path):
        """Test adapting JavaScript parsed data to InsightForge format."""
        # Create a JS file with a simple class
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        class_file = project_dir / "class.js"
        class_file.write_text("""/**
 * Test class
 */
class TestClass {
    constructor(name) {
        this.name = name;
    }
    
    /**
     * Test method
     */
    test() {
        return true;
    }
}

module.exports = { TestClass };
""")
        
        # Parse the project
        parser = JavaScriptProjectParser(project_dir=str(project_dir))
        parsed_data = parser.parse()
        
        # Adapt to InsightForge format
        insightforge_data = adapt_js_to_insightforge(parsed_data)
        
        # Check results
        assert 'classes' in insightforge_data
        assert len(insightforge_data['classes']) == 1
        assert insightforge_data['classes'][0]['name'] == 'TestClass'
        
        # Check converted methods
        assert len(insightforge_data['classes'][0]['methods']) == 2  # constructor and test
        method_names = [m['name'] for m in insightforge_data['classes'][0]['methods']]
        assert 'constructor' in method_names
        assert 'test' in method_names