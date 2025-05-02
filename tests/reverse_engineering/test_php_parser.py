"""
Tests for the PHP parser.
"""

import os
import pytest
from insightforge.reverse_engineering.php_parser import (
    PHPParser, 
    PHPProjectParser, 
    PHPClass, 
    PHPFunction, 
    adapt_php_to_insightforge,
    PHPLY_AVAILABLE
)

# Skip all tests if phply is not available
pytestmark = pytest.mark.skipif(not PHPLY_AVAILABLE, reason="phply module not available")


class TestPHPParser:
    """Test class for PHP parser."""
    
    def test_php_parser_initialization(self):
        """Test PHP parser initialization."""
        parser = PHPParser()
        assert parser.file_path is None
        
        parser = PHPParser(file_path="/path/to/file.php")
        assert parser.file_path == "/path/to/file.php"
    
    def test_php_parser_parse_empty_file(self, tmp_path):
        """Test parsing an empty PHP file."""
        # Create an empty PHP file
        empty_file = tmp_path / "empty.php"
        empty_file.write_text("<?php\n// Empty file\n")
        
        # Parse it
        parser = PHPParser(str(empty_file))
        classes, functions, metadata = parser.parse()
        
        # Check results
        assert len(classes) == 0
        assert len(functions) == 0
        assert 'namespaces' in metadata
        assert len(metadata['namespaces']) == 0
    
    def test_php_parser_parse_class(self, tmp_path):
        """Test parsing a PHP file with a class."""
        # Create a PHP file with a simple class
        class_file = tmp_path / "class.php"
        class_file.write_text("""<?php
/**
 * Test class
 */
class TestClass {
    private $property;
    
    /**
     * Test method
     */
    public function test() {
        return true;
    }
}
""")
        
        # Parse it
        parser = PHPParser(str(class_file))
        classes, functions, metadata = parser.parse()
        
        # Check results
        assert len(classes) == 1
        assert classes[0]['name'] == 'TestClass'
        assert len(classes[0]['methods']) == 1
        assert classes[0]['methods'][0]['name'] == 'test'
        assert len(classes[0]['properties']) == 1
        assert classes[0]['properties'][0]['name'] == 'property'
    
    def test_php_parser_parse_interface(self, tmp_path):
        """Test parsing a PHP file with an interface."""
        # Create a PHP file with a simple interface
        interface_file = tmp_path / "interface.php"
        interface_file.write_text("""<?php
/**
 * Test interface
 */
interface TestInterface {
    /**
     * Test method
     */
    public function test();
}
""")
        
        # Parse it
        parser = PHPParser(str(interface_file))
        classes, functions, metadata = parser.parse()
        
        # Check results
        assert len(classes) == 1
        assert classes[0]['name'] == 'TestInterface'
        assert classes[0]['is_interface'] == True
        assert len(classes[0]['methods']) == 1
        assert classes[0]['methods'][0]['name'] == 'test'
        
        # Check interface list
        assert 'interfaces' in metadata
        assert len(metadata['interfaces']) == 1
        assert 'TestInterface' in metadata['interfaces']
    
    def test_php_parser_parse_trait(self, tmp_path):
        """Test parsing a PHP file with a trait."""
        # Create a PHP file with a simple trait
        trait_file = tmp_path / "trait.php"
        trait_file.write_text("""<?php
/**
 * Test trait
 */
trait TestTrait {
    private $property;
    
    /**
     * Test method
     */
    public function test() {
        return true;
    }
}
""")
        
        # Parse it
        parser = PHPParser(str(trait_file))
        classes, functions, metadata = parser.parse()
        
        # Check results
        assert len(classes) == 1
        assert classes[0]['name'] == 'TestTrait'
        assert classes[0]['is_trait'] == True
        assert len(classes[0]['methods']) == 1
        assert classes[0]['methods'][0]['name'] == 'test'
        
        # Check trait list
        assert 'traits' in metadata
        assert len(metadata['traits']) == 1
        assert 'TestTrait' in metadata['traits']
    
    def test_php_parser_parse_function(self, tmp_path):
        """Test parsing a PHP file with a function."""
        # Create a PHP file with a simple function
        function_file = tmp_path / "function.php"
        function_file.write_text("""<?php
/**
 * Test function
 */
function test_function($param) {
    return $param;
}
""")
        
        # Parse it
        parser = PHPParser(str(function_file))
        classes, functions, metadata = parser.parse()
        
        # Check results
        assert len(classes) == 0
        assert len(functions) == 1
        assert functions[0]['name'] == 'test_function'
        assert len(functions[0]['parameters']) == 1
        assert functions[0]['parameters'][0]['name'] == 'param'
    
    def test_php_parser_parse_namespace(self, tmp_path):
        """Test parsing a PHP file with a namespace."""
        # Create a PHP file with a namespace
        namespace_file = tmp_path / "namespace.php"
        namespace_file.write_text("""<?php
namespace App\\Test;

/**
 * Test class
 */
class TestClass {
    private $property;
    
    /**
     * Test method
     */
    public function test() {
        return true;
    }
}
""")
        
        # Parse it
        parser = PHPParser(str(namespace_file))
        classes, functions, metadata = parser.parse()
        
        # Check results
        assert len(classes) == 1
        assert classes[0]['name'] == 'TestClass'
        assert classes[0]['namespace'] == 'App\\Test'
        assert classes[0]['full_name'] == 'App\\Test\\TestClass'
        
        # Check namespace list
        assert 'namespaces' in metadata
        assert len(metadata['namespaces']) == 1
        assert 'App\\Test' in metadata['namespaces']
    
    def test_php_parser_parse_inheritance(self, tmp_path):
        """Test parsing a PHP file with inheritance."""
        # Create a PHP file with inheritance
        inheritance_file = tmp_path / "inheritance.php"
        inheritance_file.write_text("""<?php
interface TestInterface {
    public function interfaceMethod();
}

trait TestTrait {
    public function traitMethod() {
        return 'trait';
    }
}

class BaseClass {
    public function baseMethod() {
        return 'base';
    }
}

class ChildClass extends BaseClass implements TestInterface {
    use TestTrait;
    
    public function interfaceMethod() {
        return 'interface';
    }
    
    public function childMethod() {
        return 'child';
    }
}
""")
        
        # Parse it
        parser = PHPParser(str(inheritance_file))
        classes, functions, metadata = parser.parse()
        
        # Check results
        assert len(classes) == 4
        
        # Find the ChildClass
        child_class = None
        for cls in classes:
            if cls['name'] == 'ChildClass':
                child_class = cls
                break
        
        assert child_class is not None
        assert len(child_class['extends']) == 1
        assert child_class['extends'][0] == 'BaseClass'
        assert len(child_class['implements']) == 1
        assert child_class['implements'][0] == 'TestInterface'
        assert len(child_class['uses']) == 1
        assert child_class['uses'][0] == 'TestTrait'
        
        # Check class dependencies
        assert 'class_dependencies' in metadata
        assert 'ChildClass' in metadata['class_dependencies']
        deps = metadata['class_dependencies']['ChildClass']
        assert 'BaseClass' in deps
        assert 'TestInterface' in deps
        assert 'TestTrait' in deps


class TestPHPProjectParser:
    """Test class for PHP project parser."""
    
    def test_php_project_parser_initialization(self):
        """Test PHP project parser initialization."""
        parser = PHPProjectParser(project_dir="/path/to/project")
        assert parser.project_dir == "/path/to/project"
        assert 'vendor' in parser.exclude_dirs
        assert '.php' in parser.file_extensions
    
    def test_php_project_parser_find_php_files(self, tmp_path):
        """Test finding PHP files in a project."""
        # Create project structure
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        # Create PHP files
        (project_dir / "file1.php").write_text("<?php\n")
        (project_dir / "file2.php").write_text("<?php\n")
        
        # Create subdirectory
        sub_dir = project_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "file3.php").write_text("<?php\n")
        
        # Create vendor directory that should be excluded
        vendor_dir = project_dir / "vendor"
        vendor_dir.mkdir()
        (vendor_dir / "vendor.php").write_text("<?php\n")
        
        # Initialize parser
        parser = PHPProjectParser(project_dir=str(project_dir))
        
        # Find PHP files
        php_files = parser._find_php_files()
        
        # Check results
        assert len(php_files) == 3
        assert str(project_dir / "file1.php") in php_files
        assert str(project_dir / "file2.php") in php_files
        assert str(sub_dir / "file3.php") in php_files
        assert str(vendor_dir / "vendor.php") not in php_files
    
    def test_adapt_php_to_insightforge(self, tmp_path):
        """Test adapting PHP parsed data to InsightForge format."""
        # Create a PHP file with a simple class
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        class_file = project_dir / "class.php"
        class_file.write_text("""<?php
namespace App\\Test;

/**
 * Test class
 */
class TestClass {
    private $property;
    
    /**
     * Test method
     */
    public function test() {
        return true;
    }
}
""")
        
        # Parse the project
        parser = PHPProjectParser(project_dir=str(project_dir))
        parsed_data = parser.parse()
        
        # Adapt to InsightForge format
        insightforge_data = adapt_php_to_insightforge(parsed_data)
        
        # Check results
        assert 'classes' in insightforge_data
        assert len(insightforge_data['classes']) == 1
        assert insightforge_data['classes'][0]['name'] == 'TestClass'
        
        # Check converted methods
        assert len(insightforge_data['classes'][0]['methods']) == 1
        assert insightforge_data['classes'][0]['methods'][0]['name'] == 'test'
        
        # Check namespace metadata
        found_namespace = False
        for attr in insightforge_data['classes'][0]['attributes']:
            if attr['name'] == '__namespace__':
                found_namespace = True
                assert attr['docstring'] == 'Namespace: App\\Test'
                break
        
        assert found_namespace, "Namespace metadata not found"