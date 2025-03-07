"""
    Generate mock media library and subtitle files (empty files)
    Folder structure:
        media_library/
            ShowName/
                Season01/
                    Episode01.mp4
                    Episode02.mp4
                Season02/
                    Episode01.mp4
                    Episode02.mp4
                ...
            ShowName2/
                Season01/
                    Episode01.mp4
                    Episode02.mp4
                ...
        subtitle_files/
            ShowName.S01E01.en.srt
            ShowName.S01E02.en.srt
            ShowName2.S01E01.en.srt
            ShowName2.S01E02.en.srt
            ...
"""

import os
import random
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
import json

# Flag to control whether to keep test files after test
KEEP_TEST_FILES = True
# Flag to control whether to create zip archives for subtitles
CREATE_ZIP_ARCHIVES = True

class TestFileGenerator:
    """Generate test files for media library and subtitles"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        # TV Shows data with seasons and episodes info
        cls.TV_SHOWS = [
            {
                "name": "Breaking Bad",
                "seasons": 5,
                "episodes_per_season": [7, 13, 13, 13, 16],
                "naming_pattern": "Breaking.Bad.S{season:02d}E{episode:02d}.1080p.BluRay.x264"
            },
            {
                "name": "Game of Thrones", 
                "seasons": 8,
                "episodes_per_season": [10, 10, 10, 10, 10, 10, 7, 6],
                "naming_pattern": "Game.of.Thrones.S{season:02d}E{episode:02d}.2160p.HBO.WEB-DL"
            },
            {
                "name": "Stranger Things",
                "seasons": 4,
                "episodes_per_season": [8, 9, 8, 9],
                "naming_pattern": "Stranger.Things.S{season:02d}E{episode:02d}.1080p.NF.WEB-DL"
            },
            {
                "name": "The Mandalorian",
                "seasons": 3,
                "episodes_per_season": [8, 8, 8],
                "naming_pattern": "The.Mandalorian.S{season:02d}E{episode:02d}.2160p.DSNP.WEB-DL"
            }
        ]

        # Possible folder structure patterns
        cls.FOLDER_PATTERNS = [
            "{show_name}/Season {season}",
            "{show_name}/S{season:02d}",
            "{show_name}/Season {season:02d}",
            "{show_name}/S{season:02d} - Season {season}"
        ]

        # File extensions
        cls.VIDEO_EXTENSIONS = [".mp4", ".mkv", ".avi"]
        cls.SUBTITLE_EXTENSIONS = [".srt", ".ass", ".ssa"]
        
        # Subtitle naming patterns
        cls.SUBTITLE_PATTERNS = [
            "{show_name}.S{season:02d}E{episode:02d}.{lang}{ext}",
            "{show_name}.{season}x{episode:02d}.{lang}{ext}",
            "{show_name}.Season{season}Episode{episode}.{lang}{ext}",
            "{show_name}.S{season:02d}.E{episode:02d}.{lang}{ext}"
        ]
        
        # Language codes
        cls.LANGUAGES = ["en", "zh", "zh-CN", "zh-TW", "ja", "ko", "es", "fr"]

        # Create test directories
        cls.test_dir = Path(__file__).parent / "test_data"
        cls.media_dir = cls.test_dir / "media_library"
        cls.subtitle_dir = cls.test_dir / "subtitle_files"

    def generate_video_files(self, show, folder_pattern):
        """Generate video files for a TV show"""
        show_path = self.media_dir / show['name']
        
        for season in range(1, show['seasons'] + 1):
            # Generate season folder using random pattern
            season_folder = folder_pattern.format(
                show_name=show['name'],
                season=season
            )
            season_path = show_path / season_folder
            season_path.mkdir(parents=True, exist_ok=True)
            
            # Generate episode files
            episodes = show['episodes_per_season'][season - 1]
            for episode in range(1, episodes + 1):
                # Random video extension
                ext = random.choice(self.VIDEO_EXTENSIONS)
                
                # Generate filename using show's naming pattern
                filename = f"{show['naming_pattern'].format(season=season, episode=episode)}{ext}"
                episode_path = season_path / filename
                
                # Create empty file
                episode_path.touch()

    def generate_subtitle_files(self, show):
        """Generate subtitle files for a TV show"""
        # Select a consistent subtitle pattern for this show
        show_subtitle_pattern = random.choice(self.SUBTITLE_PATTERNS)
        # Select a consistent subtitle extension for this show
        show_subtitle_ext = random.choice(self.SUBTITLE_EXTENSIONS)
        
        # Keep track of generated subtitle files for zip creation
        show_subtitle_files = []
        
        # Limit total subtitle files to 5
        subtitle_count = 0
        max_subtitles = 5
        
        for season in range(1, show['seasons'] + 1):
            if subtitle_count >= max_subtitles:
                break
                
            episodes = show['episodes_per_season'][season - 1]
            for episode in range(1, episodes + 1):
                if subtitle_count >= max_subtitles:
                    break
                    
                # Generate just one subtitle file per episode to stay within limit
                lang = random.choice(self.LANGUAGES)
                filename = show_subtitle_pattern.format(
                    show_name=show['name'].replace(' ', '.'),
                    season=season,
                    episode=episode,
                    lang=lang,
                    ext=show_subtitle_ext
                )
                
                subtitle_path = self.subtitle_dir / filename
                subtitle_path.touch()
                show_subtitle_files.append(subtitle_path)
                subtitle_count += 1
        
        # Create zip archive for show's subtitles if enabled
        if CREATE_ZIP_ARCHIVES:
            zip_filename = f"{show['name'].replace(' ', '_')}_subtitles.zip"
            zip_path = self.subtitle_dir / zip_filename
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for subtitle_file in show_subtitle_files:
                    # Add file to zip with relative path from subtitle_dir
                    zipf.write(subtitle_file, subtitle_file.relative_to(self.subtitle_dir))

    def generate_test_files(self):
        """Generate all test files"""
        # Clean up existing test directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        
        # Create directories
        self.media_dir.mkdir(parents=True)
        self.subtitle_dir.mkdir(parents=True)
        
        # Select random shows
        selected_shows = random.sample(self.TV_SHOWS, random.randint(2, 4))
        
        for show in selected_shows:
            # Random folder pattern for each show
            folder_pattern = random.choice(self.FOLDER_PATTERNS)
            self.generate_video_files(show, folder_pattern)
            self.generate_subtitle_files(show)
            
        return {
            'media_dir': str(self.media_dir),
            'subtitle_dir': str(self.subtitle_dir),
            'shows': [show['name'] for show in selected_shows]
        }

if __name__ == '__main__':
    generator = TestFileGenerator()
    generator.setUpClass()
    result = generator.generate_test_files()
    print(f"Test files generated successfully:")
    print(f"Media library: {result['media_dir']}")
    print(f"Subtitle files: {result['subtitle_dir']}")
    print(f"Generated shows: {', '.join(result['shows'])}")

