"""
    NeatSub main module
    Functions:
        1. Receive the subtitle file or the subtitle pack file
            1.1 Extract all the subtitle files from the subtitle pack file
        2. Then scan the media library. get the video files and the existing subtitle files
        3. Try to match the new subtitle file to the video files by ShowName, Season, Episode (fuzzy match)
        4. Move and rename the subtitle file to the video file's folder
"""

import os
import json
import logging
import shutil

import zipfile
import rarfile
import py7zr

from typing import List, Dict, Tuple
import re
from fuzzywuzzy import fuzz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_subtitle_pack(file_path: str, temp_dir: str, allowed_extensions: List[str]) -> List[str]:
    """Extract subtitle files from a compressed file."""
    extracted_files = []
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_ext == '.zip':
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        elif file_ext == '.rar':
            with rarfile.RarFile(file_path, 'r') as rar_ref:
                rar_ref.extractall(temp_dir)
        elif file_ext == '.7z':
            with py7zr.SevenZipFile(file_path, 'r') as sz_ref:
                sz_ref.extractall(temp_dir)
                
        # Walk through the temp directory to find subtitle files
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in allowed_extensions):
                    extracted_files.append(os.path.join(root, file))
                    
    except Exception as e:
        logger.error(f"Error extracting {file_path}: {str(e)}")
        raise
        
    return extracted_files

def scan_media_library(library_path: str, video_extensions: List[str]) -> List[Dict]:
    """Scan media library for video files."""
    video_files = []
    
    for root, _, files in os.walk(library_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_info = parse_video_filename(file)
                if video_info:
                    video_info['full_path'] = os.path.join(root, file)
                    video_files.append(video_info)
                    
    return video_files

def parse_video_filename(filename: str) -> Dict:
    """Parse video filename to extract show name, season, and episode information."""
    # Common patterns for TV show filenames
    patterns = [
        r'(.+?)[\. ]S(\d{1,2})E(\d{1,2})',  # ShowName.S01E01
        r'(.+?)[\. ](\d{1,2})x(\d{1,2})',    # ShowName.1x01
        r'(.+?)[\. ]Season[\. ]?(\d{1,2})[\. ]?Episode[\. ]?(\d{1,2})',  # ShowName.Season1Episode01 or ShowName Season 1 Episode 01
        r'(.+?)[\. ]Season(\d{1,2})Episode(\d{1,2})',  # ShowName.Season1Episode01
        r'(.+?)[\. ]S(\d{1,2})\.E(\d{1,2})',  # ShowName.S01.E01
    ]
    
    original_name = filename
    filename = os.path.splitext(filename)[0]
    
    # Try direct matching first, without removing language codes
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            result = {
                'show_name': match.group(1).replace('.', ' ').strip(),
                'season': int(match.group(2)),
                'episode': int(match.group(3)),
                'match_end': match.end(),
                'original_name': original_name
            }
            logger.debug(f"✓ Pattern matched: {match.group(1).strip()} S{match.group(2)}E{match.group(3)}")
            return result
    
    # If no match found, try removing language codes
    lang_pattern = r'(.+?)\.([a-zA-Z]{2,3}(-[A-Z]{2})?|[a-zA-Z]{2,3})$'
    lang_match = re.match(lang_pattern, filename)
    if lang_match:
        filename_without_lang = lang_match.group(1)
        removed_lang = lang_match.group(2)
        logger.debug(f"→ Trying without language code [{removed_lang}]: {filename_without_lang}")
        
        for pattern in patterns:
            match = re.search(pattern, filename_without_lang, re.IGNORECASE)
            if match:
                result = {
                    'show_name': match.group(1).replace('.', ' ').strip(),
                    'season': int(match.group(2)),
                    'episode': int(match.group(3)),
                    'match_end': match.end(),
                    'original_name': original_name
                }
                logger.debug(f"✓ Pattern matched after language removal: {match.group(1).strip()} S{match.group(2)}E{match.group(3)}")
                return result
    
    logger.debug(f"✗ No pattern match for: {filename}")
    return None

def match_subtitle_to_video(subtitle_file: str, video_files: List[Dict], threshold: int = 80) -> Dict:
    """Match subtitle file to the most appropriate video file."""
    subtitle_info = parse_video_filename(os.path.basename(subtitle_file))
    if not subtitle_info:
        logger.debug(f"✗ Could not parse: {os.path.basename(subtitle_file)}")
        return None
        
    logger.debug(f"→ Processing: {subtitle_info['original_name']}")
    logger.debug(f"  Show: {subtitle_info['show_name']}, S{subtitle_info['season']:02d}E{subtitle_info['episode']:02d}")
    
    best_match = None
    highest_score = 0
    
    for video in video_files:
        # First check if season and episode match
        if (subtitle_info['season'] == video['season'] and 
            subtitle_info['episode'] == video['episode']):
            # Then check show name similarity
            score = fuzz.ratio(subtitle_info['show_name'].lower(), 
                             video['show_name'].lower())
            logger.debug(f"  → Match score with {video['original_name']}: {score}")
            if score > highest_score and score >= threshold:
                highest_score = score
                best_match = video
                
    if best_match:
        logger.info(f"✓ Matched: {os.path.basename(best_match['full_path'])} (score: {highest_score})")
    else:
        logger.info(f"✗ No matching video found")
        
    return best_match

def process_subtitle_file(file_path: str, config: Dict, lang_suffix: str = "", overwrite: bool = False) -> List[Dict]:
    """Process subtitle file or pack and match with video files."""
    results = []
    
    # Convert extensions to set for faster lookup
    subtitle_exts = set(config['subtitle_file_extensions'])
    subtitle_pack_exts = set(config['subtitle_pack_extensions'])
    
    file_ext = os.path.splitext(file_path)[1].lower()
    subtitle_files = []
    
    logger.debug(f"→ Processing: {file_path}")
    
    # Handle subtitle pack
    if file_ext in subtitle_pack_exts:
        logger.debug(f"→ Extracting subtitle pack: {file_path}")
        subtitle_files.extend(
            extract_subtitle_pack(file_path, config['temp_dir'], config['subtitle_file_extensions'])
        )
    # Handle single subtitle file
    elif file_ext in subtitle_exts:
        subtitle_files.append(file_path)
    else:
        error_msg = f"✗ Unsupported file type: {file_ext}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Process each subtitle file
    for subtitle_file in subtitle_files:
        logger.debug(f"→ Processing subtitle: {os.path.basename(subtitle_file)}")
        for library in config['media_libraries']:
            logger.debug(f"  → Scanning library: {library['library_name']}")
            
            # Scan video files in the library
            video_files = scan_media_library(
                library['library_path'], 
                config['video_file_extensions']
            )
            
            # Try to match subtitle with video
            matched_video = match_subtitle_to_video(subtitle_file, video_files)
            
            if matched_video:
                # Create destination path
                video_dir = os.path.dirname(matched_video['full_path'])
                video_name = os.path.splitext(os.path.basename(matched_video['full_path']))[0]
                subtitle_ext = os.path.splitext(subtitle_file)[1]
                
                # Handle language suffix
                if lang_suffix == "*":
                    orig_name = os.path.basename(subtitle_file)
                    orig_name_no_ext = os.path.splitext(orig_name)[0]
                    
                    subtitle_info = parse_video_filename(orig_name)
                    if subtitle_info:
                        orig_suffix = orig_name_no_ext[subtitle_info['match_end']:]
                        new_subtitle_name = f"{video_name}{orig_suffix}{subtitle_ext}"
                        logger.debug(f"  → Using original suffix: {orig_suffix}")
                    else:
                        new_subtitle_name = f"{video_name}{subtitle_ext}"
                else:
                    suffix = f".{lang_suffix}" if lang_suffix else ""
                    new_subtitle_name = f"{video_name}{suffix}{subtitle_ext}"
                    logger.debug(f"  → Using language suffix: {suffix}")
                
                dest_path = os.path.join(video_dir, new_subtitle_name)
                
                # Check if destination file exists
                if os.path.exists(dest_path):
                    if not overwrite:
                        logger.info(f"✗ Skipping: {os.path.basename(subtitle_file)} (already exists)")
                        continue
                    else:
                        logger.info(f"! Overwriting: {os.path.basename(dest_path)}")
                
                # Move and rename subtitle file
                logger.debug(f"  → Moving to: {dest_path}")
                shutil.move(subtitle_file, dest_path)
                
                results.append({
                    'subtitle_file': os.path.basename(subtitle_file),
                    'matched_video': os.path.basename(matched_video['full_path']),
                    'new_location': dest_path,
                    'library': library['library_name']
                })
                
                break  # Stop searching other libraries once matched
    
    return results










