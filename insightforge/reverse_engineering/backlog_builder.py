"""
Backlog Builder Module
--------------------
Builds a task backlog from use cases and code analysis.
"""

from typing import Dict, List, Any, Optional


class UserStory:
    """Represents a user story."""
    
    def __init__(
        self, 
        id: str, 
        title: str, 
        as_a: str, 
        i_want: str, 
        so_that: str, 
        acceptance_criteria: List[str],
        points: Optional[int] = None,
        source: Optional[str] = None
    ):
        """Initialize a user story."""
        self.id = id
        self.title = title
        self.as_a = as_a
        self.i_want = i_want
        self.so_that = so_that
        self.acceptance_criteria = acceptance_criteria
        self.points = points
        self.source = source
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'title': self.title,
            'as_a': self.as_a,
            'i_want': self.i_want,
            'so_that': self.so_that,
            'acceptance_criteria': self.acceptance_criteria,
            'points': self.points,
            'source': self.source
        }
    
    def to_markdown(self) -> str:
        """Convert to markdown representation."""
        md = f"# User Story: {self.id} - {self.title}\n\n"
        md += f"**As a** {self.as_a}\n\n"
        md += f"**I want** {self.i_want}\n\n"
        md += f"**So that** {self.so_that}\n\n"
        
        md += "## Acceptance Criteria\n\n"
        for criteria in self.acceptance_criteria:
            md += f"- {criteria}\n"
        
        if self.points:
            md += f"\n**Story Points**: {self.points}\n"
        
        if self.source:
            md += f"\n**Source**: {self.source}\n"
        
        return md


class Epic:
    """Represents an epic (group of related user stories)."""
    
    def __init__(
        self,
        id: str,
        title: str,
        description: str,
        user_stories: List[str] = None  # List of user story IDs
    ):
        """Initialize an epic."""
        self.id = id
        self.title = title
        self.description = description
        self.user_stories = user_stories or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'user_stories': self.user_stories
        }
    
    def to_markdown(self) -> str:
        """Convert to markdown representation."""
        md = f"# Epic: {self.id} - {self.title}\n\n"
        md += f"{self.description}\n\n"
        
        md += "## User Stories\n\n"
        for story_id in self.user_stories:
            md += f"- {story_id}\n"
        
        return md


class BacklogBuilder:
    """Builds a product backlog from use cases and code analysis."""
    
    def __init__(self):
        """Initialize the backlog builder."""
        self.user_stories: List[UserStory] = []
        self.epics: List[Epic] = []
    
    def build_from_use_cases(self, use_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build backlog items from use cases."""
        for i, uc in enumerate(use_cases):
            # Create a user story ID
            story_id = f"US-{i+1:03d}"
            
            # Simple conversion of use case to user story
            # In a real implementation, this would be more sophisticated
            user_story = UserStory(
                id=story_id,
                title=uc.get('name', f"Story from {uc.get('id', 'unknown')}"),
                as_a="user",  # Placeholder
                i_want=uc.get('name', ""),
                so_that="I can accomplish my goal",  # Placeholder
                acceptance_criteria=[
                    "Feature works as expected",
                    "Edge cases are handled"
                ],
                source=uc.get('source')
            )
            
            self.user_stories.append(user_story)
        
        # Group stories into epics based on similarity or domain
        # This is a simplified grouping logic
        if len(self.user_stories) > 0:
            epic = Epic(
                id="EP-001",
                title="Initial Epic",
                description="First epic containing initial user stories",
                user_stories=[story.id for story in self.user_stories[:5]]  # First 5 stories
            )
            self.epics.append(epic)
        
        return {
            'user_stories': [story.to_dict() for story in self.user_stories],
            'epics': [epic.to_dict() for epic in self.epics]
        }
    
    def generate_markdown(self, output_dir: str) -> None:
        """Generate markdown files for the backlog items."""
        import os
        
        # Create directories
        stories_dir = os.path.join(output_dir, "userstories")
        epics_dir = os.path.join(output_dir, "epics")
        
        os.makedirs(stories_dir, exist_ok=True)
        os.makedirs(epics_dir, exist_ok=True)
        
        # Generate user story files
        for story in self.user_stories:
            file_path = os.path.join(stories_dir, f"{story.id}.md")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(story.to_markdown())
        
        # Generate epic files
        for epic in self.epics:
            file_path = os.path.join(epics_dir, f"{epic.id}.md")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(epic.to_markdown())