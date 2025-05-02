"""
Integration tests for the full InsightForge pipeline.
"""

import os
import tempfile
import pytest
from pathlib import Path

from insightforge.reverse_engineering.code_parser import CodeParser
from insightforge.reverse_engineering.doc_generator import DocGenerator
from insightforge.reverse_engineering.usecase_extractor import UseCaseExtractor
from insightforge.reverse_engineering.backlog_builder import BacklogBuilder
from insightforge.reverse_engineering.business_rules import BusinessRulesExtractor


class TestFullPipeline:
    """Tests for the full InsightForge pipeline."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_simple_project_pipeline(self, simple_project, temp_output_dir):
        """Test the full pipeline with a simple project."""
        # 1. Parse the project
        parser = CodeParser(str(simple_project))
        parsed_data = parser.parse()
        
        # Verify basic parsing results
        assert 'classes' in parsed_data
        assert len(parsed_data['classes']) > 0
        
        # 2. Extract use cases
        uc_extractor = UseCaseExtractor()
        use_cases = uc_extractor.extract(parsed_data)
        
        # Add use cases to parsed data
        parsed_data['usecases'] = use_cases
        
        # 3. Extract business rules
        rule_extractor = BusinessRulesExtractor()
        business_rules = rule_extractor.extract_from_parsed_data(parsed_data)
        
        # Add business rules to parsed data
        parsed_data['business_rules'] = business_rules
        
        # 4. Build backlog
        backlog_builder = BacklogBuilder()
        backlog = backlog_builder.build_from_use_cases(use_cases)
        
        # Add user stories to parsed data
        parsed_data['userstories'] = backlog['user_stories']
        
        # 5. Generate documentation
        doc_generator = DocGenerator(temp_output_dir)
        doc_generator.generate(parsed_data, "Test Project", "Test project description")
        
        # Verify documentation output
        assert os.path.exists(os.path.join(temp_output_dir, "index.md"))
        assert os.path.exists(os.path.join(temp_output_dir, "overview.md"))
        assert os.path.exists(os.path.join(temp_output_dir, "classes"))
        
        # Check if class documentation was generated
        class_files = os.listdir(os.path.join(temp_output_dir, "classes"))
        assert len(class_files) > 0
        assert "BaseClass.md" in class_files
        assert "ChildClass.md" in class_files
        
        # 6. Generate backlog markdown (optional)
        backlog_builder.user_stories = [UserStory(**story) for story in backlog['user_stories']]
        backlog_builder.generate_markdown(temp_output_dir)
        
        # Verify user story output
        assert os.path.exists(os.path.join(temp_output_dir, "userstories"))
        story_files = os.listdir(os.path.join(temp_output_dir, "userstories"))
        assert len(story_files) > 0
    
    def test_complex_project_pipeline(self, complex_project, temp_output_dir):
        """Test the full pipeline with a complex project."""
        # 1. Parse the project
        parser = CodeParser(str(complex_project))
        parsed_data = parser.parse()
        
        # Verify basic parsing results
        assert 'classes' in parsed_data
        assert len(parsed_data['classes']) >= 3  # Should find at least Model, User, and UserService
        
        # 2. Extract use cases
        uc_extractor = UseCaseExtractor()
        use_cases = uc_extractor.extract(parsed_data)
        
        # Add use cases to parsed data
        parsed_data['usecases'] = use_cases
        
        # 3. Extract business rules
        rule_extractor = BusinessRulesExtractor()
        business_rules = rule_extractor.extract_from_parsed_data(parsed_data)
        
        # Add business rules to parsed data
        parsed_data['business_rules'] = business_rules
        
        # 4. Build backlog
        backlog_builder = BacklogBuilder()
        backlog = backlog_builder.build_from_use_cases(use_cases)
        
        # Add user stories to parsed data
        parsed_data['userstories'] = backlog['user_stories']
        
        # 5. Generate documentation
        doc_generator = DocGenerator(temp_output_dir, generate_diagrams=True)
        doc_generator.generate(parsed_data, "Complex Project", "A complex project with multiple components")
        
        # Verify documentation output
        assert os.path.exists(os.path.join(temp_output_dir, "index.md"))
        assert os.path.exists(os.path.join(temp_output_dir, "overview.md"))
        assert os.path.exists(os.path.join(temp_output_dir, "classes"))
        
        # Check if class documentation was generated
        class_files = os.listdir(os.path.join(temp_output_dir, "classes"))
        assert len(class_files) >= 3
        assert "Model.md" in class_files
        assert "User.md" in class_files
        assert "UserService.md" in class_files
        
        # Check if business rules documentation was generated
        assert os.path.exists(os.path.join(temp_output_dir, "business_rules"))
        
        # Check if diagrams were generated
        assert os.path.exists(os.path.join(temp_output_dir, "diagrams"))
        
        # Check specific diagram files
        diagram_files = os.listdir(os.path.join(temp_output_dir, "diagrams"))
        assert "class_diagram.md" in diagram_files or any(f.startswith("class_diagram_") for f in diagram_files)
        
        # 6. Generate backlog markdown
        from insightforge.reverse_engineering.backlog_builder import UserStory
        backlog_builder.user_stories = [UserStory(**story) for story in backlog['user_stories']]
        backlog_builder.generate_markdown(temp_output_dir)
        
        # Verify user story output
        assert os.path.exists(os.path.join(temp_output_dir, "userstories"))
        story_files = os.listdir(os.path.join(temp_output_dir, "userstories"))
        assert len(story_files) > 0