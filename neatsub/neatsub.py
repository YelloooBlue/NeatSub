"""
    NeatSub main module
    Functions:
        1. Receive the subtitle file or the subtitle pack file
            1.1 Extract all the subtitle files from the subtitle pack file
        2. Then scan the media library. get the video files and the existing subtitle files
        3. Try to match the new subtitle file to the video files by ShowName, Season, Episode (fuzzy match)
        4. Move and rename the subtitle file to the video file's folder
"""

from typing import List, Dict
import os
import shutil  # move and rename

# Extract
import zipfile
import rarfile
import py7zr

# Match
import re
from fuzzywuzzy import fuzz  # fuzzy match (for show name)
from werkzeug.utils import secure_filename

# Logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import ConfigManager
from config_manager import ConfigManager


def extract_subtitle_pack(file_path: str, temp_dir: str, allowed_extensions: List[str]) -> List[str]:
    """ Extract subtitle files from zip, rar, 7z file """
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

    logger.debug(
        f"Extracted {len(extracted_files)} subtitle files from {file_path}")
    return extracted_files


def scan_media_library(library_path: str, video_extensions: List[str]) -> List[Dict]:
    """ Scan media library for video files """
    video_files = []  # include video info and full path

    for root, _, files in os.walk(library_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_info = parse_video_filename(file)
                if video_info:
                    video_info['full_path'] = os.path.join(
                        root, file)  # append full path
                    video_files.append(video_info)

    logger.debug(f"Found {len(video_files)} video files in {library_path}")
    return video_files


def parse_video_filename(filename: str) -> Dict:
    """ Parse video filename to get [show name, season, episode] """
    # regex patterns
    patterns = [
        r'(.+?)[\. ]S(\d{1,2})E(\d{1,2})',  # ShowName.S01E01
        r'(.+?)[\. ](\d{1,2})x(\d{1,2})',    # ShowName.1x01
        # ShowName.Season1Episode01 or ShowName Season 1 Episode 01 (maybe useless, the secure_filename will remove the spaces)
        r'(.+?)[\. ]Season[\. ]?(\d{1,2})[\. ]?Episode[\. ]?(\d{1,2})',
        # ShowName.Season1Episode01
        r'(.+?)[\. ]Season(\d{1,2})Episode(\d{1,2})',
        r'(.+?)[\. ]S(\d{1,2})\.E(\d{1,2})',  # ShowName.S01.E01
        # ShowName_S01E01_Additional_Info
        r'(.+?)[_\- ]S(\d{1,2})E(\d{1,2})[_\- ]'
    ]

    original_name = filename
    filename = os.path.splitext(filename)[0]

    # Try direct matching first, without removing language codes
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)  # case insensitive
        if match:

            # Align the show name with uploaded subtitle filename style
            show_name = match.group(1).replace('.', ' ').strip()
            secure_show_name = secure_filename(show_name)

            # extract year
            clean_show_name = re.sub(r'[^\w\s]', ' ', show_name) # remove special characters
            year_re = re.search(r'(?<!\d)(\d{4})(?![\w])', show_name) # match 4 digits not preceded or followed by a digit
            year = None
            if year_re:
                year = year_re.group(1)
                clean_show_name = re.sub(r'\b' + year + r'\b', '', clean_show_name).strip() # remove year
                clean_show_name = re.sub(r'\s+', ' ', clean_show_name).strip() # normalize spaces
                
            result = {
                'show_name': show_name,
                'secure_show_name': secure_show_name,
                'clean_show_name': clean_show_name,
                'season': int(match.group(2)),
                'episode': int(match.group(3)),
                'match_end': match.end(),   # end index of the match (for suffix parsing) TODO: remove this?
                'suffix': filename[match.end():],
                'original_name': original_name
            }

            if year:
                result['year'] = year

            logger.debug(
                f"✓ Pattern matched: {match.group(1).strip()} S{match.group(2)}E{match.group(3)}")
            return result

    logger.debug(f"✗ No pattern match for: {filename}")
    return None


def match_subtitle_to_video(subtitle_info: Dict, video_files: List[Dict], threshold: int = 80) -> Dict:
    """ Match subtitle file to the most appropriate video file """
    if not subtitle_info:
        logger.debug(f"✗ Could not parse subtitle info")
        return None

    logger.debug(f"→ Processing: {subtitle_info['original_name']}")
    logger.debug(
        f"  Show: {subtitle_info['show_name']}, S{subtitle_info['season']:02d}E{subtitle_info['episode']:02d}")

    best_match = None
    highest_score = 0

    for video in video_files:

        # First check if season and episode match (exact match)
        if (subtitle_info['season'] == video['season'] and
                subtitle_info['episode'] == video['episode']):

            # Then check show name similarity (fuzzy match)
            # score = fuzz.ratio(subtitle_info['show_name'].lower(), video['secure_show_name'].lower())
            score = fuzz.ratio(subtitle_info['clean_show_name'].lower(), video['clean_show_name'].lower())
            # Other fuzzy match functions: partial_ratio, token_sort_ratio, token_set_ratio

            # if Year exists, increase score if year matches
            if 'year' in subtitle_info and 'year' in video:
                if subtitle_info['year'] == video['year']:
                    score += 10  # boost score by 10 if year matches
                    logger.debug(f"  → Year matched: {subtitle_info['year']}")

            logger.debug(
                f"  → SubtitleName 「{subtitle_info['clean_show_name']}」 vs VideoName 「{video['clean_show_name']}」: {score}")

            if score > highest_score and score >= threshold:
                highest_score = score
                best_match = video
                best_match['match_score'] = score  # append match score

    if best_match:
        logger.info(
            f"✓ Matched: {os.path.basename(best_match['full_path'])} (score: {highest_score})")
    else:
        logger.info(f"✗ No matching video found")

    return best_match


def process_subtitle_file(file_path: str, config_manager: ConfigManager, lang_suffix: str = "", overwrite: bool = False) -> List[Dict]:
    """ Process subtitle file or pack and match with video files """
    results = []

    # Get extensions from config manager
    subtitle_exts = set(config_manager.subtitle_extensions)
    subtitle_pack_exts = set(config_manager.subtitle_pack_extensions)

    file_ext = os.path.splitext(file_path)[1].lower()
    subtitle_files = []

    logger.debug(f"→ Processing: {file_path}")

    # Handle subtitle pack
    if file_ext in subtitle_pack_exts:
        logger.debug(f"→ Extracting subtitle pack: {file_path}")
        subtitle_files.extend(
            extract_subtitle_pack(
                file_path, config_manager.temp_dir, config_manager.subtitle_extensions)
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
        logger.debug(
            f"→ Processing subtitle: {os.path.basename(subtitle_file)}")
        
        # get the subtitle info
        subtitle_info = parse_video_filename(os.path.basename(subtitle_file))
        if not subtitle_info:
            logger.debug(f"✗ Could not parse subtitle file: {subtitle_file}")
            continue

        for library in config_manager.media_libraries:
            logger.debug(f"  → Scanning library: {library['library_name']}")

            # Scan video files in the library
            video_files = scan_media_library(
                library['library_path'],
                config_manager.video_extensions
            )

            # Try to match subtitle with video
            matched_video = match_subtitle_to_video(subtitle_info, video_files)

            if matched_video:
                # Create destination path
                video_dir = os.path.dirname(matched_video['full_path'])
                video_name = os.path.splitext(
                    os.path.basename(matched_video['full_path']))[0]
                subtitle_ext = os.path.splitext(subtitle_file)[1]

                if lang_suffix == "*":
                    # Use the suffix from subtitle_info directly
                    new_subtitle_name = f"{video_name}{subtitle_info['suffix']}{subtitle_ext}"
                    logger.debug(f"  → Using original suffix: {subtitle_info['suffix']}")
                else:
                    suffix = f".{lang_suffix}" if lang_suffix else ""
                    new_subtitle_name = f"{video_name}{suffix}{subtitle_ext}"
                    logger.debug(f"  → Using language suffix: {suffix}")

                dest_path = os.path.join(video_dir, new_subtitle_name)

                status = 'Failed'
                # Check if destination file already exists
                if os.path.exists(dest_path):
                    if overwrite:
                        status = 'Overwritten'
                        logger.info(
                            f"! Overwriting: {os.path.basename(dest_path)}")
                        # Delete the original subtitle file
                        shutil.move(subtitle_file, dest_path)
                    else:
                        status = 'Skipped'
                        logger.info(
                            f"✗ Skipping: {os.path.basename(subtitle_file)} (already exists)")
                        # Delete the original subtitle file
                        os.remove(subtitle_file)

                else:
                    status = 'Moved'
                    logger.info(f"  → Moving to: {dest_path}")
                    # Delete the original subtitle file
                    shutil.move(subtitle_file, dest_path)

                results.append({
                    'status': status,
                    'subtitle_file': os.path.basename(subtitle_file),
                    'matched_video': os.path.basename(matched_video['full_path']),
                    'destination': os.path.basename(dest_path),
                    'match_score': matched_video['match_score']
                })
                break  # Stop searching other libraries once we find a match

    return results

if __name__ == '__main__':
    # Test the functions
    test_subtitle_filename = "Slow.Horses.S04E06.Hello.Goodbye.2160p.ATVP.WEB-DL.DDP5.1.H.265-NTb.ass"
    test_video_filename = "Slow Horses (2022) - S04E06 - Hello Goodbye (1080p ATVP WEB-DL x265 Ghost).mkv"

    secure_subtitle_name = secure_filename(test_subtitle_filename)

    print(f"Secure Subtitle Name: {secure_subtitle_name}")

    subtitle_info = parse_video_filename(secure_subtitle_name)
    print(subtitle_info)

    video_info = parse_video_filename(test_video_filename)
    print(video_info)

    # Test different fuzzy match functions
    score = fuzz.ratio(subtitle_info['clean_show_name'].lower(), video_info['clean_show_name'].lower())
    print(f"ratio Score: {score}")

    score = fuzz.token_set_ratio(subtitle_info['clean_show_name'].lower(), video_info['clean_show_name'].lower())
    print(f"token_set_ratio Score: {score}")

    score = fuzz.token_sort_ratio(subtitle_info['clean_show_name'].lower(), video_info['clean_show_name'].lower())
    print(f"token_sort_ratio Score: {score}")

    score = fuzz.partial_ratio(subtitle_info['clean_show_name'].lower(), video_info['clean_show_name'].lower())
    print(f"partial_ratio Score: {score}")