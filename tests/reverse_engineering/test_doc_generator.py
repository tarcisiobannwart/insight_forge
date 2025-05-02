"""
Tests for the doc_generator module.
"""

import os
import tempfile
import pytest
from pathlib import Path

from insightforge.reverse_engineering.doc_generator import DocGenerator
from insightforge.reverse_engineering.template_system import TemplateManager


class TestDocGenerator:
    """Tests for the DocGenerator class."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def mock_parsed_data(self):
        """Create sample parsed data for testing."""
        return {
            'classes': [
                {
                    'name': 'TestClass',
                    'docstring': 'Test class docstring',
                    'file_path': '/path/to/file.py',
                    'line_number': 10,
                    'methods': [
                        {
                            'name': 'test_method',
                            'docstring': 'Test method docstring',
                            'parameters': ['param1', 'param2'],
                            'line_number': 12,
                            'return_type': 'int'
                        }
                    ],
                    'attributes': [
                        {
                            'name': 'test_attr',
                            'type': 'str',
                            'is_class_var': False
                        }
                    ],
                    'base_classes': []
                }
            ],
            'functions': [
                {
                    'name': 'test_function',
                    'docstring': 'Test function docstring',
                    'parameters': ['param1', 'param2'],
                    'file_path': '/path/to/file.py',
                    'line_number': 30,
                    'return_type': 'bool'
                }
            ],
            'business_rules': [
                {
                    'id': 'BR-001',
                    'name': 'Test Business Rule',
                    'description': 'This is a test business rule',
                    'file_path': '/path/to/file.py',
                    'line_number': 15,
                    'type': 'validation',
                    'severity': 'medium',
                    'source': 'docstring',
                    'code_component': 'TestClass.test_method'
                }
            ]
        }
    
    def test_init(self):
        """Test initialization of DocGenerator."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize with default settings
            doc_gen = DocGenerator(tmpdir)
            assert doc_gen.output_dir == tmpdir
            assert doc_gen.generate_diagrams is True
            
            # Initialize with custom settings
            doc_gen = DocGenerator(tmpdir, generate_diagrams=False)
            assert doc_gen.generate_diagrams is False
    
    def test_generate_overview(self, temp_output_dir, mock_parsed_data):
        """Test generating an overview document."""
        # Initialize DocGenerator
        doc_gen = DocGenerator(temp_output_dir)
        
        # Test private method directly
        doc_gen._generate_overview(mock_parsed_data)
        
        # Check if overview file was created
        overview_path = os.path.join(temp_output_dir, "overview.md")
        assert os.path.exists(overview_path)
        
        # Check content of overview file
        with open(overview_path, 'r') as f:
            content = f.read()
            assert "Project Overview" in content
            assert "Classes" in content
            assert "TestClass" in content
            assert "Functions" in content
            assert "test_function" in content
    
    def test_generate_class_docs(self, temp_output_dir, mock_parsed_data):
        """Test generating class documentation."""
        # Initialize DocGenerator
        doc_gen = DocGenerator(temp_output_dir)
        
        # Test private method directly
        doc_gen._generate_class_docs(mock_parsed_data['classes'])
        
        # Check if class directory was created
        classes_dir = os.path.join(temp_output_dir, "classes")
        assert os.path.exists(classes_dir)
        
        # Check if class file was created
        class_path = os.path.join(classes_dir, "TestClass.md")
        assert os.path.exists(class_path)
        
        # Check content of class file
        with open(class_path, 'r') as f:
            content = f.read()
            assert "Class: TestClass" in content
            assert "Test class docstring" in content
            assert "test_method" in content
            assert "test_attr" in content
    
    def test_generate_function_docs(self, temp_output_dir, mock_parsed_data):
        """Test generating function documentation."""
        # Initialize DocGenerator
        doc_gen = DocGenerator(temp_output_dir)
        
        # Test private method directly
        doc_gen._generate_function_docs(mock_parsed_data['functions'])
        
        # Check if functions directory was created
        functions_dir = os.path.join(temp_output_dir, "functions")
        assert os.path.exists(functions_dir)
        
        # Check if function file was created
        function_path = os.path.join(functions_dir, "test_function.md")
        assert os.path.exists(function_path)
        
        # Check content of function file
        with open(function_path, 'r') as f:
            content = f.read()
            assert "Function: `test_function" in content
            assert "Test function docstring" in content
            assert "param1" in content
            assert "param2" in content
    
    def test_generate_business_rule_docs(self, temp_output_dir, mock_parsed_data):
        """Test generating business rule documentation."""
        # Initialize DocGenerator
        doc_gen = DocGenerator(temp_output_dir)
        
        # Test private method directly
        doc_gen._generate_business_rule_docs(mock_parsed_data['business_rules'])
        
        # Check if business_rules directory was created
        rules_dir = os.path.join(temp_output_dir, "business_rules")
        assert os.path.exists(rules_dir)
        
        # Check if business rule file was created
        rule_path = os.path.join(rules_dir, "BR-001.md")
        assert os.path.exists(rule_path)
        
        # Check content of business rule file
        with open(rule_path, 'r') as f:
            content = f.read()
            assert "Business Rule: BR-001" in content
            assert "Test Business Rule" in content
            assert "This is a test business rule" in content
            assert "validation" in content
            assert "medium" in content
    
    def test_generate_with_real_templates(self, temp_output_dir, mock_parsed_data):
        """Test generating documentation with actual templates."""
        # Initialize DocGenerator
        doc_gen = DocGenerator(temp_output_dir, generate_diagrams=False)
        
        # Generate all documentation
        doc_gen.generate(mock_parsed_data, "Test Project", "This is a test project")
        
        # Check that index file was created
        index_path = os.path.join(temp_output_dir, "index.md")
        assert os.path.exists(index_path)
        
        # Check content of index file
        with open(index_path, 'r') as f:
            content = f.read()
            assert "Test Project Documentation" in content
            assert "This is a test project" in content
            assert "Classes" in content
            assert "Functions" in content
            assert "Business Rules" in content
    
    def test_customize_template(self, temp_output_dir):
        """Test customizing a template."""
        # Initialize DocGenerator
        doc_gen = DocGenerator(temp_output_dir)
        
        # Test customizing a template
        custom_template = "# Custom Template: {{ class.name }}"
        result = doc_gen.customize_template("class.md.j2", custom_template)
        
        # Check if customization was successful
        assert result is True
        
        # Check if custom template was created in the right location
        templates_dir = os.path.join(temp_output_dir, "_templates")
        template_path = os.path.join(templates_dir, "class.md.j2")
        assert os.path.exists(template_path)
        
        # Check content of custom template
        with open(template_path, 'r') as f:
            content = f.read()
            assert content == custom_template


class TestDocGeneratorWithDiagrams:
    """Tests for the DocGenerator class with diagram generation."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def mock_parsed_data_with_modules(self):
        """Create sample parsed data with modules for testing diagrams."""
        return {
            'classes': [
                {
                    'name': 'ClassA',
                    'docstring': 'Class A',
                    'file_path': '/path/to/module1/file1.py',
                    'line_number': 10,
                    'methods': [],
                    'attributes': [],
                    'base_classes': []
                },
                {
                    'name': 'ClassB',
                    'docstring': 'Class B',
                    'file_path': '/path/to/module1/file2.py',
                    'line_number': 20,
                    'methods': [],
                    'attributes': [],
                    'base_classes': ['ClassA']
                }
            ],
            'modules': [
                {
                    'name': 'module1',
                    'file_path': '/path/to/module1'
                },
                {
                    'name': 'module2',
                    'file_path': '/path/to/module2'
                }
            ],
            'dependencies': [
                {
                    'source': 'module1',
                    'target': 'module2'
                }
            ],
            'flows': {
                'test_flow': {
                    'participants': ['User', 'System'],
                    'steps': [
                        {
                            'source': 'User',
                            'target': 'System',
                            'message': 'Request data'
                        }
                    ]
                }
            }
        }
    
    def test_generate_diagrams(self, temp_output_dir, mock_parsed_data_with_modules):
        """Test generating diagrams."""
        # Initialize DocGenerator with diagrams enabled
        doc_gen = DocGenerator(temp_output_dir, generate_diagrams=True)
        
        # Test _generate_diagrams method
        doc_gen._generate_diagrams(mock_parsed_data_with_modules)
        
        # Check if diagrams directory was created
        diagrams_dir = os.path.join(temp_output_dir, "diagrams")
        assert os.path.exists(diagrams_dir)
        
        # Check if diagram index was created
        index_path = os.path.join(diagrams_dir, "index.md")
        assert os.path.exists(index_path)
        
        # Check if class diagram was created
        class_diagram_path = os.path.join(diagrams_dir, "class_diagram.md")
        assert os.path.exists(class_diagram_path)
        
        # Check if module diagram was created
        module_diagram_path = os.path.join(diagrams_dir, "module_diagram.md")
        assert os.path.exists(module_diagram_path)
        
        # Check if sequence diagram was created
        sequence_diagram_path = os.path.join(diagrams_dir, "sequence_test_flow.md")
        assert os.path.exists(sequence_diagram_path)