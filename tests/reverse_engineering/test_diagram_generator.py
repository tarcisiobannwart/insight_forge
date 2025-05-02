"""
Tests for the diagram generator module.
"""

import os
import tempfile
import pytest
from pathlib import Path

from insightforge.reverse_engineering.diagram_generator import DiagramGenerator, DiagramIndex


class TestDiagramGenerator:
    """Tests for the DiagramGenerator class."""
    
    def setup_method(self):
        """Set up test fixture."""
        self.generator = DiagramGenerator(max_items_per_diagram=5)
        
        # Sample parsed data
        self.sample_classes = [
            {
                'name': 'TestClass',
                'docstring': 'A test class',
                'file_path': '/path/to/file.py',
                'line_number': 10,
                'base_classes': ['BaseClass'],
                'methods': [
                    {
                        'name': 'test_method',
                        'docstring': 'A test method',
                        'parameters': ['param1', 'param2'],
                        'line_number': 12
                    }
                ],
                'attributes': [
                    {
                        'name': 'attr1',
                        'type': 'str'
                    }
                ]
            },
            {
                'name': 'AnotherClass',
                'docstring': 'Another class',
                'file_path': '/path/to/another_file.py',
                'line_number': 20,
                'base_classes': ['BaseClass'],
                'methods': [],
                'attributes': []
            }
        ]
        
        self.sample_modules = [
            {
                'name': 'module1',
                'file_path': '/path/to/module1.py'
            },
            {
                'name': 'module2',
                'file_path': '/path/to/module2.py'
            }
        ]
        
        self.sample_dependencies = [
            {
                'source': 'module1',
                'target': 'module2'
            }
        ]
        
        self.sample_flow = {
            'main_flow': {
                'name': 'Main Flow',
                'description': 'The main flow',
                'participants': ['User', 'System'],
                'steps': [
                    {
                        'source': 'User',
                        'target': 'System',
                        'message': 'Request data',
                        'response': 'Return data'
                    }
                ]
            }
        }
        
        self.parsed_data = {
            'classes': self.sample_classes,
            'modules': self.sample_modules,
            'dependencies': self.sample_dependencies,
            'flows': self.sample_flow
        }
    
    def test_generate_class_diagram(self):
        """Test generating a class diagram."""
        # Generate diagram
        diagram = self.generator.generate_class_diagram(
            self.parsed_data,
            include_methods=True,
            include_attributes=True
        )
        
        # Check that the diagram is a string and contains mermaid syntax
        assert isinstance(diagram, str)
        assert diagram.startswith("```mermaid")
        assert diagram.endswith("```")
        assert "classDiagram" in diagram
        
        # Check that the diagram contains the classes
        assert "TestClass" in diagram
        assert "AnotherClass" in diagram
        
        # Check that inheritance relationships are shown
        assert "BaseClass <|-- TestClass" in diagram
        assert "BaseClass <|-- AnotherClass" in diagram
        
        # Check that methods and attributes are included when requested
        assert "test_method(param1, param2)" in diagram
        assert "+attr1 : str" in diagram
    
    def test_generate_class_diagram_without_details(self):
        """Test generating a class diagram without methods and attributes."""
        # Generate diagram
        diagram = self.generator.generate_class_diagram(
            self.parsed_data,
            include_methods=False,
            include_attributes=False
        )
        
        # Check that the diagram is a string and contains mermaid syntax
        assert isinstance(diagram, str)
        assert "classDiagram" in diagram
        
        # Check that methods and attributes are not included
        assert "test_method" not in diagram
        assert "attr1" not in diagram
    
    def test_generate_module_diagram(self):
        """Test generating a module diagram."""
        # Generate diagram
        diagram = self.generator.generate_module_diagram(
            self.parsed_data,
            group_by_package=True
        )
        
        # Check that the diagram is a string and contains mermaid syntax
        assert isinstance(diagram, str)
        assert "graph TD" in diagram
        
        # Check that modules are included
        assert "module1" in diagram
        assert "module2" in diagram
        
        # Check that dependencies are shown
        assert "module1" in diagram
        assert "module2" in diagram
        assert "-->" in diagram
    
    def test_generate_sequence_diagram(self):
        """Test generating a sequence diagram."""
        # Add a flow to the parsed data
        data = self.parsed_data.copy()
        data['flows'] = {
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
        
        # Generate diagram
        diagram = self.generator.generate_sequence_diagram(
            data,
            'test_flow'
        )
        
        # Check that the diagram is a string and contains mermaid syntax
        assert isinstance(diagram, str)
        assert "sequenceDiagram" in diagram
        
        # Check that participants and steps are included
        assert "participant User" in diagram
        assert "participant System" in diagram
        assert "User->>+System: Request data" in diagram
    
    def test_clean_id(self):
        """Test cleaning IDs for use in Mermaid diagrams."""
        # Test cleaning various IDs
        assert self.generator._clean_id("module.name") == "module_name"
        assert self.generator._clean_id("name-with-dashes") == "name_with_dashes"
        assert self.generator._clean_id("name with spaces") == "name_with_spaces"
    
    def test_get_package_name(self):
        """Test extracting package name from module name."""
        # Test extracting package names
        assert self.generator._get_package_name("package.module") == "package"
        assert self.generator._get_package_name("standalone") == "root"
        assert self.generator._get_package_name("a.b.c") == "a"
    
    def test_is_external(self):
        """Test checking if a module is external."""
        # Test checking for external modules
        assert self.generator._is_external("os") is True
        assert self.generator._is_external("sys") is True
        assert self.generator._is_external("custom_module") is False
        assert self.generator._is_external("os.path") is True


class TestDiagramIndex:
    """Tests for the DiagramIndex class."""
    
    def setup_method(self):
        """Set up test fixture."""
        self.temp_dir = tempfile.mkdtemp()
        self.index = DiagramIndex(self.temp_dir)
        
        # Create the diagrams directory
        diagrams_dir = os.path.join(self.temp_dir, "diagrams")
        os.makedirs(diagrams_dir, exist_ok=True)
    
    def teardown_method(self):
        """Tear down test fixture."""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_add_class_diagram(self):
        """Test adding a class diagram to the index."""
        # Add a class diagram to the index
        self.index.add_class_diagram(
            "Test Class Diagram",
            "diagrams/class_diagram.md",
            ["TestClass", "AnotherClass"]
        )
        
        # Check that the diagram was added
        assert len(self.index.class_diagrams) == 1
        assert self.index.class_diagrams[0]['name'] == "Test Class Diagram"
        assert self.index.class_diagrams[0]['path'] == "diagrams/class_diagram.md"
        assert self.index.class_diagrams[0]['classes'] == ["TestClass", "AnotherClass"]
    
    def test_add_module_diagram(self):
        """Test adding a module diagram to the index."""
        # Add a module diagram to the index
        self.index.add_module_diagram(
            "Test Module Diagram",
            "diagrams/module_diagram.md",
            ["module1", "module2"]
        )
        
        # Check that the diagram was added
        assert len(self.index.module_diagrams) == 1
        assert self.index.module_diagrams[0]['name'] == "Test Module Diagram"
        assert self.index.module_diagrams[0]['path'] == "diagrams/module_diagram.md"
        assert self.index.module_diagrams[0]['modules'] == ["module1", "module2"]
    
    def test_add_sequence_diagram(self):
        """Test adding a sequence diagram to the index."""
        # Add a sequence diagram to the index
        self.index.add_sequence_diagram(
            "Test Sequence Diagram",
            "diagrams/sequence_diagram.md",
            "test_flow"
        )
        
        # Check that the diagram was added
        assert len(self.index.sequence_diagrams) == 1
        assert self.index.sequence_diagrams[0]['name'] == "Test Sequence Diagram"
        assert self.index.sequence_diagrams[0]['path'] == "diagrams/sequence_diagram.md"
        assert self.index.sequence_diagrams[0]['flow'] == "test_flow"
    
    def test_generate_index_markdown(self):
        """Test generating Markdown for the index."""
        # Add diagrams to the index
        self.index.add_class_diagram(
            "Test Class Diagram",
            "diagrams/class_diagram.md",
            ["TestClass", "AnotherClass"]
        )
        self.index.add_module_diagram(
            "Test Module Diagram",
            "diagrams/module_diagram.md",
            ["module1", "module2"]
        )
        self.index.add_sequence_diagram(
            "Test Sequence Diagram",
            "diagrams/sequence_diagram.md",
            "test_flow"
        )
        
        # Generate Markdown
        markdown = self.index.generate_index_markdown()
        
        # Check that the Markdown contains the expected sections
        assert "# Diagram Index" in markdown
        assert "## Class Diagrams" in markdown
        assert "## Module Diagrams" in markdown
        assert "## Sequence Diagrams" in markdown
        
        # Check that the Markdown contains the diagram links
        assert "[Test Class Diagram](diagrams/class_diagram.md)" in markdown
        assert "[Test Module Diagram](diagrams/module_diagram.md)" in markdown
        assert "[Test Sequence Diagram](diagrams/sequence_diagram.md)" in markdown
    
    def test_save_index(self):
        """Test saving the index to a file."""
        # Add a diagram to the index
        self.index.add_class_diagram(
            "Test Class Diagram",
            "diagrams/class_diagram.md",
            ["TestClass", "AnotherClass"]
        )
        
        # Save the index
        index_path = self.index.save_index()
        
        # Check that the file was created
        assert os.path.exists(index_path)
        
        # Check that the file contains the expected content
        with open(index_path, 'r') as f:
            content = f.read()
            assert "# Diagram Index" in content
            assert "## Class Diagrams" in content
            assert "[Test Class Diagram](diagrams/class_diagram.md)" in content