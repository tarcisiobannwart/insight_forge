"""
Use Case Extractor Module
-----------------------
Extracts use cases from parsed code and documentation.
"""

import re
from typing import Dict, List, Any, Optional


class UseCaseExtractor:
    """Extracts use cases from parsed code and documentation."""
    
    def __init__(self):
        """Initialize the use case extractor."""
        pass
    
    def extract(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract use cases from parsed data."""
        use_cases = []
        
        # Extract from classes and their docstrings
        for cls in parsed_data.get('classes', []):
            uc_from_class = self._extract_from_docstring(
                cls.get('name', ''), 
                cls.get('docstring', ''),
                cls.get('file_path', '')
            )
            if uc_from_class:
                use_cases.extend(uc_from_class)
            
            # Also look at methods
            for method in cls.get('methods', []):
                uc_from_method = self._extract_from_docstring(
                    f"{cls.get('name', '')}.{method.get('name', '')}",
                    method.get('docstring', ''),
                    cls.get('file_path', '')
                )
                if uc_from_method:
                    use_cases.extend(uc_from_method)
        
        # Extract from functions
        for func in parsed_data.get('functions', []):
            uc_from_func = self._extract_from_docstring(
                func.get('name', ''), 
                func.get('docstring', ''),
                func.get('file_path', '')
            )
            if uc_from_func:
                use_cases.extend(uc_from_func)
        
        return use_cases
    
    def _extract_from_docstring(
        self, name: str, docstring: Optional[str], file_path: str
    ) -> List[Dict[str, Any]]:
        """Extract use cases from a docstring."""
        if not docstring:
            return []
        
        use_cases = []
        
        # Look for Use Case: pattern in docstrings
        uc_pattern = r"(?:Use[- ]?[Cc]ase|UC)[:\s]+([^\n]+)"
        matches = re.finditer(uc_pattern, docstring)
        
        for match in matches:
            use_case_desc = match.group(1).strip()
            
            # Generate a unique ID based on name
            uc_id = f"UC-{abs(hash(name + use_case_desc)) % 1000:03d}"
            
            use_cases.append({
                'id': uc_id,
                'name': use_case_desc,
                'source': name,
                'file_path': file_path,
                'description': docstring.strip()
            })
        
        return use_cases