"""
    Storage(cache json) file reading and writing
"""

import json
import os
from typing import List, Dict, Any, Optional


class Storage:
    """Base class for JSON storage operations"""
    
    def __init__(self, storage_path: str):
        """
        Initialize Storage with a path to the JSON file
        
        Args:
            storage_path (str): Path to the JSON storage file
        """
        self.storage_path = storage_path
        self._ensure_storage_file()
    
    def _ensure_storage_file(self) -> None:
        """Ensure the storage file exists, create if it doesn't"""
        if not os.path.exists(self.storage_path):
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            self.save([])
    
    def load(self) -> List[Dict[str, Any]]:
        """Load data from the JSON file"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    
    def save(self, data: List[Dict[str, Any]]) -> None:
        """Save data to the JSON file"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


class MediaLibrariesStorage(Storage):
    """Class for managing media libraries storage"""
    
    def __init__(self, storage_path: str):
        super().__init__(storage_path)
    
    def get_all_libraries(self) -> List[Dict[str, Any]]:
        """Get all media libraries"""
        return self.load()
    
    def add_library(self, library_data: Dict[str, Any]) -> None:
        """
        Add a new media library
        
        Args:
            library_data (dict): Library information including name, path, etc.
        """
        libraries = self.load()
        # Check if library with same name already exists
        if any(lib["library_name"] == library_data["library_name"] for lib in libraries):
            raise ValueError(f"Library with name '{library_data['library_name']}' already exists")
        libraries.append(library_data)
        self.save(libraries)
    
    def update_library(self, library_name: str, updated_data: Dict[str, Any]) -> None:
        """
        Update an existing media library
        
        Args:
            library_name (str): Name of the library to update
            updated_data (dict): Updated library information
        """
        libraries = self.load()
        for i, library in enumerate(libraries):
            if library["library_name"] == library_name:
                libraries[i].update(updated_data)
                self.save(libraries)
                return
        raise ValueError(f"Library '{library_name}' not found")
    
    def remove_library(self, library_name: str) -> None:
        """
        Remove a media library
        
        Args:
            library_name (str): Name of the library to remove
        """
        libraries = self.load()
        libraries = [lib for lib in libraries if lib["library_name"] != library_name]
        self.save(libraries)
    
    def get_library(self, library_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific library by name
        
        Args:
            library_name (str): Name of the library to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Library information if found, None otherwise
        """
        libraries = self.load()
        for library in libraries:
            if library["library_name"] == library_name:
                return library
        return None

