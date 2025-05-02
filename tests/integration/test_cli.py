"""
Integration tests for the CLI interface.
"""

import os
import pytest
import subprocess
import tempfile
from pathlib import Path


@pytest.mark.cli
class TestCLI:
    """Tests for the command-line interface."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_cli_help(self):
        """Test that the CLI help command works."""
        # Run the CLI with --help flag
        result = subprocess.run(
            ["python", "main.py", "--help"],
            capture_output=True,
            text=True
        )
        
        # Check that the help output contains expected text
        assert result.returncode == 0
        assert "InsightForge" in result.stdout
        assert "usage:" in result.stdout
        assert "--output" in result.stdout
    
    def test_cli_version(self):
        """Test that the CLI version command works."""
        # Run the CLI with --version flag
        result = subprocess.run(
            ["python", "main.py", "--version"],
            capture_output=True,
            text=True
        )
        
        # Check that the version output is as expected
        assert result.returncode == 0
        assert "InsightForge" in result.stdout
        assert "v" in result.stdout  # Version number should start with v
    
    def test_cli_simple_analysis(self, simple_project, temp_output_dir):
        """Test analyzing a simple project with the CLI."""
        # Run the CLI with a project path
        result = subprocess.run(
            [
                "python", "main.py",
                "--project", str(simple_project),
                "--output", temp_output_dir,
                "--no-diagrams"  # Skip diagrams for faster tests
            ],
            capture_output=True,
            text=True
        )
        
        # Check that the command succeeded
        assert result.returncode == 0
        
        # Check that files were generated
        assert os.path.exists(os.path.join(temp_output_dir, "index.md"))
        assert os.path.exists(os.path.join(temp_output_dir, "overview.md"))
        assert os.path.exists(os.path.join(temp_output_dir, "classes"))
        
        # Check the content of the generated classes directory
        class_files = os.listdir(os.path.join(temp_output_dir, "classes"))
        assert "BaseClass.md" in class_files
        assert "ChildClass.md" in class_files