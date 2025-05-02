"""
Tests for the template system module.
"""

import os
import tempfile
import pytest
from pathlib import Path

from insightforge.reverse_engineering.template_system import TemplateLoader, TemplateManager


class TestTemplateLoader:
    """Tests for the TemplateLoader class."""
    
    def test_init_with_defaults(self):
        """Test initialization with default values."""
        loader = TemplateLoader()
        assert loader.custom_dir is None
        assert os.path.basename(loader.default_dir) == "templates"
    
    def test_init_with_custom_dir(self):
        """Test initialization with custom directory."""
        custom_dir = os.path.join(
            os.path.dirname(__file__), "templates", "custom")
        loader = TemplateLoader(custom_dir)
        assert loader.custom_dir == custom_dir
    
    def test_get_template_standard(self):
        """Test getting a standard template."""
        standard_dir = os.path.join(
            os.path.dirname(__file__), "templates", "standard")
        loader = TemplateLoader(standard_dir)
        
        # This should find the template in the standard dir
        template = loader.get_template("test.md.j2")
        assert template is not None
        
        # Render the template
        result = template.render(var="Test Value")
        assert result == "STANDARD TEMPLATE: Test Value"
    
    def test_get_template_custom(self):
        """Test getting a custom template that overrides standard."""
        standard_dir = os.path.join(
            os.path.dirname(__file__), "templates", "standard")
        custom_dir = os.path.join(
            os.path.dirname(__file__), "templates", "custom")
        
        # Create a loader with both dirs
        loader = TemplateLoader(custom_dir)
        loader.default_dir = standard_dir
        
        # Set up the choice loader manually for testing
        from jinja2 import FileSystemLoader, ChoiceLoader
        loader.env.loader = ChoiceLoader([
            FileSystemLoader(custom_dir),
            FileSystemLoader(standard_dir),
        ])
        
        # Load a custom template that exists in custom dir
        template = loader.get_template("test_custom.md.j2")
        assert template is not None
        
        # Render the template
        result = template.render(var="Custom Value")
        assert result == "CUSTOM TEMPLATE: Custom Value"
    
    def test_template_not_found(self):
        """Test error when template not found."""
        loader = TemplateLoader()
        
        # This should raise a ValueError
        with pytest.raises(ValueError):
            loader.get_template("nonexistent_template.md.j2")
    
    def test_render_template(self):
        """Test rendering a template with context."""
        standard_dir = os.path.join(
            os.path.dirname(__file__), "templates", "standard")
        loader = TemplateLoader(standard_dir)
        
        result = loader.render_template("test.md.j2", {"var": "Rendered Value"})
        assert result == "STANDARD TEMPLATE: Rendered Value"
    
    def test_template_exists(self):
        """Test checking if a template exists."""
        standard_dir = os.path.join(
            os.path.dirname(__file__), "templates", "standard")
        loader = TemplateLoader(standard_dir)
        
        # Template exists
        assert loader.template_exists("test.md.j2") is True
        
        # Template doesn't exist
        assert loader.template_exists("nonexistent.md.j2") is False
    
    def test_markdown_escape_filter(self):
        """Test the markdown_escape filter."""
        loader = TemplateLoader()
        
        # Create a simple template using the filter
        from jinja2 import Template
        template = Template('{{ text|markdown_escape }}')
        template.environment = loader.env
        
        # Test with special characters
        result = template.render(text="# Heading with *emphasis* and [link](url)")
        assert result == "\\# Heading with \\*emphasis\\* and \\[link\\]\\(url\\)"
    
    def test_pluralize_filter(self):
        """Test the pluralize filter."""
        loader = TemplateLoader()
        
        # Create a simple template using the filter
        from jinja2 import Template
        template = Template('{{ count }} {{ word|pluralize(count) }}')
        template.environment = loader.env
        
        # Test singular
        result = template.render(count=1, word="item")
        assert result == "1 item"
        
        # Test plural
        result = template.render(count=2, word="item")
        assert result == "2 items"
        
        # Test special cases
        result = template.render(count=2, word="class")
        assert result == "2 classes"
    
    def test_format_code_filter(self):
        """Test the format_code filter."""
        loader = TemplateLoader()
        
        # Create a simple template using the filter
        from jinja2 import Template
        template = Template('{{ code|format_code(lang) }}')
        template.environment = loader.env
        
        # Test formatting code
        code = "def hello():\n    print('Hello')"
        result = template.render(code=code, lang="python")
        assert result == f"```python\n{code}\n```"
    
    def test_titleize_filter(self):
        """Test the titleize filter."""
        loader = TemplateLoader()
        
        # Create a simple template using the filter
        from jinja2 import Template
        template = Template('{{ text|titleize }}')
        template.environment = loader.env
        
        # Test title case
        result = template.render(text="this is a test")
        assert result == "This Is A Test"
        
        # Test with acronyms
        result = template.render(text="using the api for xml")
        assert result == "Using The API For XML"


class TestTemplateManager:
    """Tests for the TemplateManager class."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_init(self):
        """Test initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TemplateManager(tmpdir)
            assert manager.output_dir == tmpdir
            assert manager.loader is not None
    
    def test_render_class(self, temp_output_dir):
        """Test rendering class documentation."""
        manager = TemplateManager(temp_output_dir)
        
        # Mock the render_template method
        original_render = manager.loader.render_template
        manager.loader.render_template = lambda name, context: f"Rendered {name} with {context['class']['name']}"
        
        # Prepare test data
        class_data = {
            "name": "TestClass",
            "docstring": "Test class docstring",
            "file_path": "/path/to/file.py",
            "line_number": 10
        }
        
        # Render class documentation
        output_path = manager.render_class(class_data)
        
        # Verify the file was created
        assert os.path.exists(output_path)
        with open(output_path, 'r') as f:
            content = f.read()
            assert content == "Rendered class.md.j2 with TestClass"
        
        # Restore original method
        manager.loader.render_template = original_render
    
    def test_render_function(self, temp_output_dir):
        """Test rendering function documentation."""
        manager = TemplateManager(temp_output_dir)
        
        # Mock the render_template method
        original_render = manager.loader.render_template
        manager.loader.render_template = lambda name, context: f"Rendered {name} with {context['function']['name']}"
        
        # Prepare test data
        function_data = {
            "name": "test_function",
            "docstring": "Test function docstring",
            "file_path": "/path/to/file.py",
            "line_number": 20,
            "parameters": ["param1", "param2"]
        }
        
        # Render function documentation
        output_path = manager.render_function(function_data)
        
        # Verify the file was created
        assert os.path.exists(output_path)
        with open(output_path, 'r') as f:
            content = f.read()
            assert content == "Rendered function.md.j2 with test_function"
        
        # Restore original method
        manager.loader.render_template = original_render
    
    def test_render_business_rule(self, temp_output_dir):
        """Test rendering business rule documentation."""
        manager = TemplateManager(temp_output_dir)
        
        # Mock the render_template method
        original_render = manager.loader.render_template
        manager.loader.render_template = lambda name, context: f"Rendered {name} with {context['rule']['id']}"
        
        # Prepare test data
        rule_data = {
            "id": "BR-001",
            "name": "Test Rule",
            "description": "Test rule description",
            "file_path": "/path/to/file.py",
            "line_number": 30,
            "type": "validation",
            "severity": "medium"
        }
        
        # Render business rule documentation
        output_path = manager.render_business_rule(rule_data)
        
        # Verify the file was created
        assert os.path.exists(output_path)
        with open(output_path, 'r') as f:
            content = f.read()
            assert content == "Rendered businessrule.md.j2 with BR-001"
        
        # Restore original method
        manager.loader.render_template = original_render
    
    def test_render_overview(self, temp_output_dir):
        """Test rendering overview documentation."""
        manager = TemplateManager(temp_output_dir)
        
        # Mock the render_template method
        original_render = manager.loader.render_template
        manager.loader.render_template = lambda name, context: f"Rendered {name} with {len(context['classes'])} classes"
        
        # Prepare test data
        parsed_data = {
            "classes": [
                {"name": "Class1"},
                {"name": "Class2"}
            ],
            "functions": [
                {"name": "func1"}
            ]
        }
        
        # Render overview documentation
        output_path = manager.render_overview(parsed_data)
        
        # Verify the file was created
        assert os.path.exists(output_path)
        with open(output_path, 'r') as f:
            content = f.read()
            assert content == "Rendered overview.md.j2 with 2 classes"
        
        # Restore original method
        manager.loader.render_template = original_render
    
    def test_render_index(self, temp_output_dir):
        """Test rendering index documentation."""
        manager = TemplateManager(temp_output_dir)
        
        # Mock the render_template method
        original_render = manager.loader.render_template
        manager.loader.render_template = lambda name, context: f"Rendered {name} with {context['project_name']}"
        
        # Prepare test data
        parsed_data = {
            "classes": [{"name": "Class1"}],
            "functions": [{"name": "func1"}]
        }
        
        # Render index documentation
        output_path = manager.render_index(parsed_data, "Test Project", "Project description")
        
        # Verify the file was created
        assert os.path.exists(output_path)
        with open(output_path, 'r') as f:
            content = f.read()
            assert content == "Rendered index.md.j2 with Test Project"
        
        # Restore original method
        manager.loader.render_template = original_render