"""
Tests for the usecase_extractor module.
"""

import os
import tempfile
import pytest
from pathlib import Path

from insightforge.reverse_engineering.usecase_extractor import UseCaseExtractor


class TestUseCaseExtractor:
    """Tests for the UseCaseExtractor class."""
    
    def setup_method(self):
        """Set up test fixture."""
        self.extractor = UseCaseExtractor()
    
    @pytest.fixture
    def sample_parsed_data(self):
        """Create sample parsed data for testing."""
        return {
            'classes': [
                {
                    'name': 'TestClass',
                    'docstring': 'A test class.\n\nUse Case: UC-001 Test the parser',
                    'file_path': '/path/to/file.py',
                    'line_number': 10,
                    'methods': [
                        {
                            'name': 'test_method',
                            'docstring': 'A test method.\n\nUse Case: UC-002 Test method functionality',
                            'parameters': ['param1'],
                            'line_number': 12
                        }
                    ]
                }
            ],
            'functions': [
                {
                    'name': 'test_function',
                    'docstring': 'A test function.\n\nUse Case: Process data',
                    'parameters': ['param1'],
                    'file_path': '/path/to/file.py',
                    'line_number': 30
                }
            ]
        }
    
    def test_init(self):
        """Test initialization of UseCaseExtractor."""
        extractor = UseCaseExtractor()
        # No real initialization to test, but make sure it instantiates
        assert isinstance(extractor, UseCaseExtractor)
    
    def test_extract_from_docstring(self):
        """Test extracting use cases from docstring."""
        # Test with a simple use case
        docstring = "This is a test.\n\nUse Case: Test extraction"
        result = self.extractor._extract_from_docstring("TestComponent", docstring, "/path/to/file.py")
        
        assert len(result) == 1
        assert result[0]['name'] == "Test extraction"
        assert result[0]['source'] == "TestComponent"
        assert result[0]['file_path'] == "/path/to/file.py"
        
        # Test with multiple use cases
        docstring = "This is a test.\n\nUse Case: First use case\nUse Case: Second use case"
        result = self.extractor._extract_from_docstring("TestComponent", docstring, "/path/to/file.py")
        
        assert len(result) == 2
        assert result[0]['name'] == "First use case"
        assert result[1]['name'] == "Second use case"
        
        # Test with no use cases
        docstring = "This is a test with no use cases."
        result = self.extractor._extract_from_docstring("TestComponent", docstring, "/path/to/file.py")
        
        assert len(result) == 0
        
        # Test with different formats
        docstring = "This is a test.\n\nUseCase: One format\nUC: Another format"
        result = self.extractor._extract_from_docstring("TestComponent", docstring, "/path/to/file.py")
        
        assert len(result) == 2
        
        # Test with empty/None docstring
        result = self.extractor._extract_from_docstring("TestComponent", "", "/path/to/file.py")
        assert len(result) == 0
        
        result = self.extractor._extract_from_docstring("TestComponent", None, "/path/to/file.py")
        assert len(result) == 0
    
    def test_extract_from_parsed_data(self, sample_parsed_data):
        """Test extracting use cases from parsed data."""
        result = self.extractor.extract(sample_parsed_data)
        
        # Should extract 3 use cases: 1 from class, 1 from method, 1 from function
        assert len(result) == 3
        
        # Check class use case
        class_uc = next((uc for uc in result if uc['source'] == 'TestClass'), None)
        assert class_uc is not None
        assert "Test the parser" in class_uc['name']
        
        # Check method use case
        method_uc = next((uc for uc in result if uc['source'] == 'TestClass.test_method'), None)
        assert method_uc is not None
        assert "Test method functionality" in method_uc['name']
        
        # Check function use case
        func_uc = next((uc for uc in result if uc['source'] == 'test_function'), None)
        assert func_uc is not None
        assert "Process data" in func_uc['name']
    
    def test_extract_with_empty_data(self):
        """Test extracting from empty data."""
        # Empty dictionary
        result = self.extractor.extract({})
        assert len(result) == 0
        
        # Missing keys
        result = self.extractor.extract({'other_data': []})
        assert len(result) == 0
        
        # Empty lists
        result = self.extractor.extract({'classes': [], 'functions': []})
        assert len(result) == 0
    
    def test_extract_with_real_code(self, complex_project):
        """Test extracting use cases from a real project structure."""
        # Import the CodeParser to parse the complex_project
        from insightforge.reverse_engineering.code_parser import CodeParser
        
        # Parse the project
        parser = CodeParser(str(complex_project))
        parsed_data = parser.parse()
        
        # Extract use cases
        result = self.extractor.extract(parsed_data)
        
        # The complex_project fixture has use cases in the docstrings
        assert len(result) > 0
        
        # Check for specific use cases
        uc_ids = [uc['id'] for uc in result]
        uc_names = [uc['name'] for uc in result]
        
        assert any("UC-001" in name or "Testing the parser" in name for name in uc_names)
        assert any("UC-002" in name or "User management" in name for name in uc_names)
        assert any("UC-003" in name or "User authentication" in name for name in uc_names)