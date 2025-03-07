# Media Library
"""
    Handles media library file scanning, cache reading and writing
    Supports scheduled/manual scanning
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional


class MediaLibrary:
    def __init__(self, media_dir: str, cache_dir: str, scan_interval: int = 3600,
                 video_extensions: set[str] = None, subtitle_extensions: set[str] = None):
        
        self.media_dir = media_dir
        self.cache_dir = cache_dir
        self.scan_interval = scan_interval

        self.video_extensions = video_extensions or {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'}
        self.subtitle_extensions = subtitle_extensions or {'.srt', '.ass', '.ssa', '.sub', '.idx'}

        os.makedirs(cache_dir, exist_ok=True)   # Ensure cache directory exists

    def _parse_show_info(self, filename: str) -> Optional[Dict]:
        """Parse show information from filename"""
        # Remove extension
        name = os.path.splitext(filename)[0]

        # Common season patterns
        season_patterns = [
            r'[Ss](\d{1,2})',  # S01, s01
            r'[Ss]eason\s*(\d{1,2})',  # Season 1
            r'[Ss]eason\s*(\d{1,2})',  # Season1
        ]

        # Common episode patterns
        episode_patterns = [
            r'[Ee](\d{1,3})',  # E01, e01
            r'[Ee]pisode\s*(\d{1,3})',  # Episode 1
            r'[Ee]pisode\s*(\d{1,3})',  # Episode1
        ]

        # Try to match season and episode numbers
        season_match = None
        episode_match = None
        season_pos = -1
        episode_pos = -1

        # Find positions of season and episode
        for pattern in season_patterns:
            season_match = re.search(pattern, name)
            if season_match:
                season_pos = season_match.start()
                break

        for pattern in episode_patterns:
            episode_match = re.search(pattern, name)
            if episode_match:
                episode_pos = episode_match.start()
                break

        if not season_match or not episode_match:
            return None

        season_num = int(season_match.group(1))
        episode_num = int(episode_match.group(1))

        # Extract show name (keep only the part before season info)
        show_name = name[:season_pos].strip()

        # Clean special characters from show name
        show_name = re.sub(r'[._-]', ' ', show_name).strip()

        return {
            'show_name': show_name,
            'season_number': season_num,
            'episode_number': episode_num
        }

    def _find_subtitles(self, video_path: str) -> List[Dict]:
        """Find subtitle files for the video"""
        video_dir = os.path.dirname(video_path)
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        subtitles = []

        # Search directory for subtitle files
        for file in os.listdir(video_dir):
            if not any(file.endswith(ext) for ext in self.subtitle_extensions):
                continue

            # Check if filename is related to the video
            if file.startswith(video_name):
                # Extract language identifier between video name and subtitle extension
                for ext in self.subtitle_extensions:
                    if file.endswith(ext):
                        # Remove video name and extension to get language identifier
                        language = file[len(video_name):-len(ext)]
                        if language.startswith('.'):
                            language = language[1:]  # Remove leading dot
                        subtitles.append({
                            'subtitle_file': file,
                            'language': language
                        })
                        break

        return subtitles

    def scan_media(self):
        """Scan media library and generate cache"""
        library_data = {
            'library_name': os.path.basename(self.media_dir),
            'last_update': int(datetime.now().timestamp()),
            'version': '1.0',
            'shows': []
        }

        # Used for temporary storage of show information
        shows_dict = {}

        # Iterate over media directory
        for root, _, files in os.walk(self.media_dir):
            for file in files:
                if not any(file.endswith(ext) for ext in self.video_extensions):
                    continue

                file_path = os.path.join(root, file)
                show_info = self._parse_show_info(file)

                if not show_info:
                    continue

                show_name = show_info['show_name']
                season_num = show_info['season_number']
                episode_num = show_info['episode_number']

                # Initialize show data structure
                if show_name not in shows_dict:
                    shows_dict[show_name] = {
                        'show_name': show_name,
                        'seasons': {}
                    }

                # Initialize season data structure
                if season_num not in shows_dict[show_name]['seasons']:
                    shows_dict[show_name]['seasons'][season_num] = {
                        'season_number': season_num,
                        'episodes': {}
                    }

                # Add episode information
                shows_dict[show_name]['seasons'][season_num]['episodes'][episode_num] = {
                    'episode_number': episode_num,
                    'video_file': os.path.splitext(file)[0],
                    'subtitles': self._find_subtitles(file_path)
                }

        # Convert data structure to final format
        for show in shows_dict.values():
            show_data = {
                'show_name': show['show_name'],
                'seasons': []
            }

            # Sort seasons
            for season_num in sorted(show['seasons'].keys()):
                season = show['seasons'][season_num]
                season_data = {
                    'season_number': season['season_number'],
                    'episodes': []
                }

                # Sort episodes
                for episode_num in sorted(season['episodes'].keys()):
                    season_data['episodes'].append(
                        season['episodes'][episode_num])

                show_data['seasons'].append(season_data)

            library_data['shows'].append(show_data)

        # Save cache file
        cache_file = os.path.join(
            self.cache_dir, 'cache_' + os.path.basename(self.media_dir) + '.json')
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(library_data, f, ensure_ascii=False, indent=2)

        return library_data
