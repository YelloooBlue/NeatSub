"""
    Configuration manager for NeatSub
"""
import os
import json
from typing import List, Dict

class ConfigManager:
    DEFAULT_CONFIG = {
        "version": "1.0",
        "video_file_extensions": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"],
        "subtitle_file_extensions": [".srt", ".ass", ".ssa"],
        "subtitle_pack_extensions": [".zip", ".rar", ".7z"],
        "temp_dir": "/.tmp",
        "media_libraries": [
            {
                "library_name": "Default Library",
                "library_path": "/media"
            }
        ]
    }

    def __init__(self, config_path: str):
        self._config_path = config_path
        self._config = self._load_or_create_config()

    def _load_or_create_config(self) -> Dict:
        """Load existing config or create new one with default settings"""
        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
            # Create new config file with default settings
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

    def _save_config(self, config: Dict) -> None:
        """Save configuration to file"""
        try:
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            raise Exception(f"Error saving config: {str(e)}")

    @property
    def version(self) -> str:
        """Get config version"""
        return self._config.get("version", "1.0")

    @property
    def video_extensions(self) -> List[str]:
        """Get supported video file extensions"""
        return self._config.get("video_file_extensions", self.DEFAULT_CONFIG["video_file_extensions"])

    @video_extensions.setter
    def video_extensions(self, extensions: List[str]) -> None:
        """Set supported video file extensions"""
        self._config["video_file_extensions"] = extensions
        self._save_config(self._config)

    @property
    def subtitle_extensions(self) -> List[str]:
        """Get supported subtitle file extensions"""
        return self._config.get("subtitle_file_extensions", self.DEFAULT_CONFIG["subtitle_file_extensions"])

    @subtitle_extensions.setter
    def subtitle_extensions(self, extensions: List[str]) -> None:
        """Set supported subtitle file extensions"""
        self._config["subtitle_file_extensions"] = extensions
        self._save_config(self._config)

    @property
    def subtitle_pack_extensions(self) -> List[str]:
        """Get supported subtitle pack file extensions"""
        return self._config.get("subtitle_pack_extensions", self.DEFAULT_CONFIG["subtitle_pack_extensions"])

    @subtitle_pack_extensions.setter
    def subtitle_pack_extensions(self, extensions: List[str]) -> None:
        """Set supported subtitle pack file extensions"""
        self._config["subtitle_pack_extensions"] = extensions
        self._save_config(self._config)

    @property
    def temp_dir(self) -> str:
        """Get temporary directory path"""
        return self._config.get("temp_dir", self.DEFAULT_CONFIG["temp_dir"])

    @temp_dir.setter
    def temp_dir(self, temp_dir: str) -> None:
        """Set temporary directory path"""
        self._config["temp_dir"] = temp_dir
        self._save_config(self._config)

    @property
    def media_libraries(self) -> List[Dict]:
        """Get media library configurations"""
        return self._config.get("media_libraries", [])
    
    @media_libraries.setter
    def media_libraries(self, libraries: List[Dict]) -> None:
        """Set media library configurations"""
        self._config["media_libraries"] = libraries
        self._save_config(self._config)

    def add_media_library(self, library_name: str, library_path: str) -> None:
        """Add a new media library"""
        if "media_libraries" not in self._config:
            self._config["media_libraries"] = []
        self._config["media_libraries"].append({
            "library_name": library_name,
            "library_path": library_path
        })
        self._save_config(self._config)

    def remove_media_library(self, library_name: str) -> None:
        """Remove a media library by name"""
        self._config["media_libraries"] = [
            lib for lib in self._config["media_libraries"]
            if lib["library_name"] != library_name
        ]
        self._save_config(self._config)

    def get_config_info(self) -> str:
        """Get a string representation of the current configuration"""
        return json.dumps(self._config, indent=4)






