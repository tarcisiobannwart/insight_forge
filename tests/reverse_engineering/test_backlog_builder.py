"""
Tests for the backlog_builder module.
"""

import os
import tempfile
import pytest
from pathlib import Path

from insightforge.reverse_engineering.backlog_builder import BacklogBuilder, UserStory, Epic


class TestUserStory:
    """Tests for the UserStory class."""
    
    def test_init(self):
        """Test initializing a UserStory."""
        story = UserStory(
            id="US-001",
            title="Test User Story",
            as_a="developer",
            i_want="to test the UserStory class",
            so_that="I can ensure it works correctly",
            acceptance_criteria=["Test passes", "Code is well-structured"],
            points=3,
            source="TestSource"
        )
        
        assert story.id == "US-001"
        assert story.title == "Test User Story"
        assert story.as_a == "developer"
        assert story.i_want == "to test the UserStory class"
        assert story.so_that == "I can ensure it works correctly"
        assert len(story.acceptance_criteria) == 2
        assert story.points == 3
        assert story.source == "TestSource"
    
    def test_to_dict(self):
        """Test converting a UserStory to dictionary."""
        story = UserStory(
            id="US-001",
            title="Test User Story",
            as_a="developer",
            i_want="to test the UserStory class",
            so_that="I can ensure it works correctly",
            acceptance_criteria=["Test passes"],
            points=3
        )
        
        story_dict = story.to_dict()
        
        assert story_dict['id'] == "US-001"
        assert story_dict['title'] == "Test User Story"
        assert story_dict['as_a'] == "developer"
        assert story_dict['i_want'] == "to test the UserStory class"
        assert story_dict['so_that'] == "I can ensure it works correctly"
        assert story_dict['acceptance_criteria'] == ["Test passes"]
        assert story_dict['points'] == 3
    
    def test_to_markdown(self):
        """Test converting a UserStory to markdown."""
        story = UserStory(
            id="US-001",
            title="Test User Story",
            as_a="developer",
            i_want="to test the UserStory class",
            so_that="I can ensure it works correctly",
            acceptance_criteria=["Test passes", "Code is well-structured"],
            points=3,
            source="TestSource"
        )
        
        markdown = story.to_markdown()
        
        assert "# User Story: US-001 - Test User Story" in markdown
        assert "**As a** developer" in markdown
        assert "**I want** to test the UserStory class" in markdown
        assert "**So that** I can ensure it works correctly" in markdown
        assert "- Test passes" in markdown
        assert "- Code is well-structured" in markdown
        assert "**Story Points**: 3" in markdown
        assert "**Source**: TestSource" in markdown


class TestEpic:
    """Tests for the Epic class."""
    
    def test_init(self):
        """Test initializing an Epic."""
        epic = Epic(
            id="EP-001",
            title="Test Epic",
            description="This is a test epic",
            user_stories=["US-001", "US-002"]
        )
        
        assert epic.id == "EP-001"
        assert epic.title == "Test Epic"
        assert epic.description == "This is a test epic"
        assert epic.user_stories == ["US-001", "US-002"]
    
    def test_init_without_stories(self):
        """Test initializing an Epic without user stories."""
        epic = Epic(
            id="EP-001",
            title="Test Epic",
            description="This is a test epic"
        )
        
        assert epic.user_stories == []
    
    def test_to_dict(self):
        """Test converting an Epic to dictionary."""
        epic = Epic(
            id="EP-001",
            title="Test Epic",
            description="This is a test epic",
            user_stories=["US-001", "US-002"]
        )
        
        epic_dict = epic.to_dict()
        
        assert epic_dict['id'] == "EP-001"
        assert epic_dict['title'] == "Test Epic"
        assert epic_dict['description'] == "This is a test epic"
        assert epic_dict['user_stories'] == ["US-001", "US-002"]
    
    def test_to_markdown(self):
        """Test converting an Epic to markdown."""
        epic = Epic(
            id="EP-001",
            title="Test Epic",
            description="This is a test epic",
            user_stories=["US-001", "US-002"]
        )
        
        markdown = epic.to_markdown()
        
        assert "# Epic: EP-001 - Test Epic" in markdown
        assert "This is a test epic" in markdown
        assert "## User Stories" in markdown
        assert "- US-001" in markdown
        assert "- US-002" in markdown


class TestBacklogBuilder:
    """Tests for the BacklogBuilder class."""
    
    def setup_method(self):
        """Set up test fixture."""
        self.backlog_builder = BacklogBuilder()
    
    @pytest.fixture
    def sample_use_cases(self):
        """Create sample use cases for testing."""
        return [
            {
                'id': 'UC-001',
                'name': 'Analyze code structure',
                'source': 'CodeAnalyzer',
                'description': 'Analyzes the structure of Python code',
                'file_path': '/path/to/file.py'
            },
            {
                'id': 'UC-002',
                'name': 'Generate documentation',
                'source': 'DocGenerator',
                'description': 'Generates Markdown documentation',
                'file_path': '/path/to/file.py'
            },
            {
                'id': 'UC-003',
                'name': 'Extract business rules',
                'source': 'RuleExtractor',
                'description': 'Extracts business rules from code',
                'file_path': '/path/to/file.py'
            }
        ]
    
    def test_init(self):
        """Test initialization of BacklogBuilder."""
        assert self.backlog_builder.user_stories == []
        assert self.backlog_builder.epics == []
    
    def test_build_from_use_cases(self, sample_use_cases):
        """Test building backlog items from use cases."""
        result = self.backlog_builder.build_from_use_cases(sample_use_cases)
        
        # Check user stories
        assert 'user_stories' in result
        assert len(result['user_stories']) == 3
        assert len(self.backlog_builder.user_stories) == 3
        
        # Check epics
        assert 'epics' in result
        assert len(result['epics']) == 1
        assert len(self.backlog_builder.epics) == 1
        
        # Check user story details
        story = result['user_stories'][0]
        assert story['id'] == 'US-001'
        assert 'title' in story
        assert 'as_a' in story
        assert 'i_want' in story
        assert 'so_that' in story
        assert 'acceptance_criteria' in story
        assert 'source' in story
        
        # Check epic details
        epic = result['epics'][0]
        assert epic['id'] == 'EP-001'
        assert 'title' in epic
        assert 'description' in epic
        assert 'user_stories' in epic
        
        # Check that stories are linked to the epic
        for story_id in epic['user_stories']:
            assert any(s['id'] == story_id for s in result['user_stories'])
    
    def test_build_from_empty_use_cases(self):
        """Test building from empty use cases list."""
        result = self.backlog_builder.build_from_use_cases([])
        
        assert 'user_stories' in result
        assert len(result['user_stories']) == 0
        assert 'epics' in result
        assert len(result['epics']) == 0
    
    def test_generate_markdown(self, sample_use_cases, tmp_path):
        """Test generating markdown files."""
        # Build the backlog
        self.backlog_builder.build_from_use_cases(sample_use_cases)
        
        # Generate markdown
        output_dir = tmp_path / "output"
        self.backlog_builder.generate_markdown(str(output_dir))
        
        # Check that directories were created
        stories_dir = output_dir / "userstories"
        epics_dir = output_dir / "epics"
        
        assert stories_dir.exists()
        assert epics_dir.exists()
        
        # Check that files were created
        assert (stories_dir / "US-001.md").exists()
        assert (stories_dir / "US-002.md").exists()
        assert (stories_dir / "US-003.md").exists()
        assert (epics_dir / "EP-001.md").exists()
        
        # Check content of a file
        with open(stories_dir / "US-001.md", 'r') as f:
            content = f.read()
            assert "# User Story: US-001" in content