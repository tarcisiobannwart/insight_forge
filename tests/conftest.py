"""
Shared fixtures for InsightForge tests.
"""

import os
import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def simple_python_file():
    """Fixture providing content of a simple Python file."""
    return """
class SimpleClass:
    \"\"\"A simple class for testing.
    
    Use Case: Testing the parser
    \"\"\"
    
    def __init__(self, value):
        self.value = value
        
    def get_value(self):
        \"\"\"Return the stored value.\"\"\"
        return self.value
"""


@pytest.fixture
def class_with_inheritance():
    """Fixture providing content of a Python file with class inheritance."""
    return """
class BaseClass:
    \"\"\"A base class.\"\"\"
    
    def base_method(self):
        \"\"\"A method in the base class.\"\"\"
        pass

class ChildClass(BaseClass):
    \"\"\"A child class that inherits from BaseClass.\"\"\"
    
    def child_method(self):
        \"\"\"A method in the child class.\"\"\"
        pass
"""


@pytest.fixture
def class_with_attributes():
    """Fixture providing content of a Python file with various attributes."""
    return """
class AttributeClass:
    \"\"\"A class with various attributes.\"\"\"
    
    # Class variable
    class_var = "class value"
    
    def __init__(self):
        # Instance variables
        self.instance_var1 = "instance value 1"
        self.instance_var2 = 123
    
    def method(self):
        # Local variable (not an attribute)
        local_var = "local value"
        # Using an instance variable
        return self.instance_var1
"""


@pytest.fixture
def class_with_docstring_business_rules():
    """Fixture providing content with business rules in docstrings."""
    return """
class PaymentService:
    \"\"\"Handles payment processing.
    
    Business Rule: Payments must be validated before processing
    Business Rule: Failed payments must be logged
    \"\"\"
    
    def process_payment(self, amount, user_id):
        \"\"\"Process a payment for the specified amount.
        
        Args:
            amount: The payment amount
            user_id: The user's ID
            
        Business Rule: Payment amount must be positive
        \"\"\"
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
            
        # Process payment logic
        return True
"""


@pytest.fixture
def temp_python_file(request):
    """
    Create a temporary Python file with given content.
    
    Usage:
        def test_function(temp_python_file):
            file_path = temp_python_file("print('hello')")
            # use file_path
    """
    def _create_temp_file(content):
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w+', delete=False) as temp:
            temp.write(content)
            temp.flush()
            temp_path = temp.name
        
        # Register finalizer to clean up the file
        request.addfinalizer(lambda: os.unlink(temp_path) if os.path.exists(temp_path) else None)
        
        return temp_path
    
    return _create_temp_file


@pytest.fixture
def simple_project(tmp_path):
    """
    Create a simple Python project structure for testing.
    
    Returns:
        Path to the project directory
    """
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create a file with a base class
    base_file = project_dir / "base.py"
    base_file.write_text("""
class BaseClass:
    \"\"\"A base class in the test project.
    
    Use Case: UC-001 Testing the parser
    \"\"\"
    
    def base_method(self):
        \"\"\"Base method documentation.\"\"\"
        pass
""")
    
    # Create a file with a child class
    child_file = project_dir / "child.py"
    child_file.write_text("""
from base import BaseClass

class ChildClass(BaseClass):
    \"\"\"A child class that imports and inherits from BaseClass.
    
    Business Rule: Child must call parent methods
    \"\"\"
    
    def child_method(self):
        \"\"\"Child method documentation.\"\"\"
        # First call parent method
        self.base_method()
        # Then do additional work
        pass
""")
    
    # Create a file with utility functions
    utils_file = project_dir / "utils.py"
    utils_file.write_text("""
\"\"\"Utility functions module.\"\"\"

def helper_function(value):
    \"\"\"A helper function.
    
    Args:
        value: The value to process
        
    Returns:
        Processed value
    \"\"\"
    return value * 2
""")
    
    return project_dir


@pytest.fixture
def complex_project(tmp_path):
    """
    Create a more complex Python project with multiple modules.
    
    Returns:
        Path to the project directory
    """
    project_dir = tmp_path / "complex_project"
    project_dir.mkdir()
    
    # Create a module directory
    module_dir = project_dir / "mymodule"
    module_dir.mkdir()
    
    # Add __init__.py
    init_file = module_dir / "__init__.py"
    init_file.write_text('"""My module package."""')
    
    # Create models module
    models_dir = module_dir / "models"
    models_dir.mkdir()
    
    # Add models/__init__.py
    models_init = models_dir / "__init__.py"
    models_init.write_text('"""Models subpackage."""')
    
    # Create a base model file
    base_model = models_dir / "base.py"
    base_model.write_text("""
\"\"\"Base model definitions.\"\"\"

class Model:
    \"\"\"Base model class.
    
    Business Rule: All models must have an ID
    \"\"\"
    
    def __init__(self, id=None):
        \"\"\"Initialize with optional ID.\"\"\"
        if id is None:
            raise ValueError("ID is required")
        self.id = id
    
    def save(self):
        \"\"\"Save the model.
        
        Business Rule: Models must be validated before saving
        \"\"\"
        self.validate()
        # Save logic here
        
    def validate(self):
        \"\"\"Validate the model.\"\"\"
        pass
""")
    
    # Create a user model file
    user_model = models_dir / "user.py"
    user_model.write_text("""
\"\"\"User model definition.\"\"\"

from .base import Model

class User(Model):
    \"\"\"User model.
    
    Use Case: UC-002 User management
    Business Rule: Usernames must be unique
    \"\"\"
    
    def __init__(self, id, username, email):
        \"\"\"Initialize a user.\"\"\"
        super().__init__(id)
        self.username = username
        self.email = email
        
    def validate(self):
        \"\"\"Validate user data.\"\"\"
        super().validate()
        if not self.username:
            raise ValueError("Username is required")
        if not self.email:
            raise ValueError("Email is required")
""")
    
    # Create a services module
    services_dir = module_dir / "services"
    services_dir.mkdir()
    
    # Add services/__init__.py
    services_init = services_dir / "__init__.py"
    services_init.write_text('"""Services subpackage."""')
    
    # Create a user service file
    user_service = services_dir / "user_service.py"
    user_service.write_text("""
\"\"\"User service implementation.\"\"\"

from ..models.user import User

class UserService:
    \"\"\"Service for managing users.
    
    Use Case: UC-003 User authentication
    \"\"\"
    
    def __init__(self, db_connection):
        \"\"\"Initialize with a database connection.\"\"\"
        self.db = db_connection
        
    def create_user(self, username, email):
        \"\"\"Create a new user.
        
        Business Rule: Email must be valid
        \"\"\"
        # Validate email format
        if "@" not in email:
            raise ValueError("Invalid email format")
            
        # Generate user ID
        user_id = self._generate_id()
        
        # Create and save user
        user = User(user_id, username, email)
        user.save()
        
        return user
        
    def _generate_id(self):
        \"\"\"Generate a unique ID.\"\"\"
        # ID generation logic
        return "USR-" + "123"  # Simplified for testing
""")
    
    # Create a main application file
    app_file = project_dir / "app.py"
    app_file.write_text("""
\"\"\"Main application entry point.\"\"\"

from mymodule.services.user_service import UserService

def main():
    \"\"\"Application entry point.\"\"\"
    # Initialize services
    db_connection = {"host": "localhost", "db": "users"}
    user_service = UserService(db_connection)
    
    # Use services
    try:
        user = user_service.create_user("testuser", "test@example.com")
        print(f"Created user: {user.username}")
    except ValueError as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
""")
    
    return project_dir