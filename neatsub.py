#
# Author: YelloooBlue
# Date: 2024-10-22
#

import os
import re

# Define
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm', '.m4v', '.ts', '.3gp', '.3g2', '.m2ts', '.mts', '.f4v', '.vob', '.rmvb', '.ogv', '.ogg', '.mpg', '.mpeg', '.mpe', '.mpv', '.m2v', '.m4v', '.m2v', '.m1v', '.m2p', '.m2t', '.mp2v', '.mpv2', '.mp2', '.mpa', '.m1v', '.m2v'}
SUBTITLE_EXTENSIONS = {'.srt', '.sub', '.smi', '.ssa', '.ass', '.vtt'}
SUBTITLE_LANGUAGES = {'zh-CN','en'}

#========== Files Processing ==========#

def is_path_effective(path):
    return os.path.exists(path) and os.path.isdir(path)

class VideoSubFile:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.extension = os.path.splitext(path)[1]
        self.metadata = get_file_name_metadata(self.name)

# Scan all video files in the directory
def scan_video_files(path):
    print("Scan media files in the directory: ", path)

    if (not os.path.exists(path)) or (not os.path.isdir(path)):
        print("Invalid path: ", path)
        return

    video_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:
                video_files.append(VideoSubFile(os.path.join(root, file)))

    return video_files

# Scan all subtitle files in the directory
def scan_subtitle_files(path):
    print("Scan subtitle files in the directory: ", path)

    if (not os.path.exists(path)) or (not os.path.isdir(path)):
        print("Invalid path: ", path)
        return

    subtitle_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1].lower() in SUBTITLE_EXTENSIONS:
                subtitle_files.append(VideoSubFile(os.path.join(root, file)))

    return subtitle_files

#========== MetaData Processing ==========#

class FileNameMetadata:
    def __init__(self, show_name, season, episode):
        self.show_name = show_name
        self.season = season
        self.episode = episode

def get_file_name_metadata(filename):
    name_without_ext = os.path.splitext(filename)[0] # Remove the extension
    parts = name_without_ext.split('.')
    
    
    pattern = r'S(\d+)E(\d+)' # S01E01
    
    # Basic Metadata
    show_name = []
    season = None
    episode = None
    
    for i, part in enumerate(parts):
        match = re.match(pattern, part)
        if match:
            season = int(match.group(1))
            episode = int(match.group(2))

            # The show name is the part before the season and episode
            show_name = parts[:i]
            break
    
    show_name = ' '.join(show_name)
    
    if season is not None and episode is not None:
        return FileNameMetadata(show_name, season, episode)
    else:
        return None

#========== Matching Processing ==========#

class MatchingRelation:
    def __init__(self, video, subtitle):
        self.video = video
        self.subtitle = subtitle
    
#========== Main Function ==========#

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# main
if __name__ == '__main__':
    clear_screen()

    print()
    print("@@@@@ Hello, This is NeatSub - A smart subtitle organizer @@@@@")
    print()


    #Video List
    path = input("Step 1. Please enter the directory which contains the [video] files: ")
    video_files = scan_video_files(path)

    for file in video_files:
        print("\t - %s = %s S%s E%s" % (file.name, file.metadata.show_name, file.metadata.season, file.metadata.episode))
    print("Scan Video completed!, Total video files: ", len(video_files))

    #Subtitle List
    print()
    path = input("Step 2. Please enter the directory which contains the [subtitle] files: ")
    subtitle_files = scan_subtitle_files(path)

    subtitle_exts = set()
    for file in subtitle_files:
        print("\t - %s = %s S%s E%s [%s]" % (file.name, file.metadata.show_name, file.metadata.season, file.metadata.episode, file.extension))
        subtitle_exts.add(file.extension.lower())

    print("Scan Subtitle completed!, Total subtitle files: ", len(subtitle_files))

    # A Package may contain multiple formats of subtitles
    # TODO: A Package may contain enforce subtitles，CC subtitles, etc. (may be distinguished by the file size)
    # TODO: A Package may contain multiple languages of subtitles

    # Check if there are more than one subtitle extension
    if len(subtitle_exts) > 1:
        print()
        print("Multiple subtitle extensions found: ")
        print ("\t0. All")
        for i, ext in enumerate(subtitle_exts):
            print("\t%d. [%s]" % (i+1, ext))
        
        selection = input("Step 2-1. Please select the subtitle extension to process: ")
        
        clear_screen()
        print ("Filter Subtitle Files: ")

        if selection.isdigit() and int(selection) >= 0 and int(selection) <= len(subtitle_exts):
            if int(selection) != 0:
                selected_ext = list(subtitle_exts)[int(selection)-1]
                subtitle_files = [file for file in subtitle_files if file.extension.lower() == selected_ext]

        for file in subtitle_files:
             print("\t - %s = %s S%s E%s [%s]" % (file.name, file.metadata.show_name, file.metadata.season, file.metadata.episode, file.extension))

        print("Filter Subtitle Done!", "Total subtitle files: ", len(subtitle_files))


    # Step 3. Match the video files with the subtitle files
    # Press Any Key to Continue

    input("Press any key to start matching the video files with the subtitle files...")
    clear_screen()
    
    # Match the video files with the subtitle files
    print()
    print("Step 3. Match video files with subtitle files...")

    # Check if the show name, season, and episode match

    matched_relations = []
    unmatched_videos = []


    # Try Exact Match
    for video in video_files:

        matched = False

        for subtitle in subtitle_files:
            if video.metadata.show_name == subtitle.metadata.show_name and video.metadata.season == subtitle.metadata.season and video.metadata.episode == subtitle.metadata.episode:
                # print("Matched: ", video.name, subtitle.name)
                print("\tMatched: %s ==> %s" % (video.name, subtitle.name))
                matched_relations.append(MatchingRelation(video, subtitle))
                matched = True

        if not matched:
            print("\tNot Matched: ", video.name)
            unmatched_videos.append(video)

    # Check If not all files are matched
    if len(unmatched_videos) > 0:
        print("Not all files are matched.")
        #input("Step 3-1. Do you want to [ignore the show name] and match the rest of the files? (Y/N)")

        ignore_show_name = input("Step 3-1. Do you want to [ignore the show name] and match the rest of the files? (Y/N)")

        if ignore_show_name.lower() == 'y':
            # Try Match without show name
            for video in unmatched_videos:

                matched = False

                for subtitle in subtitle_files:
                    if video.metadata.season == subtitle.metadata.season and video.metadata.episode == subtitle.metadata.episode:
                        print("\tMatched: %s ==> %s" % (video.name, subtitle.name))
                        matched_relations.append(MatchingRelation(video, subtitle))
                        matched = True

                if not matched:
                    print("\tNot Matched: ", video.name)



    if len(matched_relations) == 0:
        print("No matched relations found!")
        exit()


    print()
    print ("Matched Relations: ")

    last_video = None
    for relation in matched_relations:
        # print(relation.video.name,"==>", relation.subtitle.name)
        # if one video has multiple subtitles, dont print the video name multiple times
        if last_video != relation.video.name:
            # print(relation.video.name, "==>", relation.subtitle.name)
            print("\t%s ==> %s" % (relation.video.name, relation.subtitle.name))
            last_video = relation.video.name
        else:
            print("\t%s ==> %s" % (" "*len(relation.video.name), relation.subtitle))


    print("Match completed!", "Total matched relations: ", len(matched_relations))


    # Step 4. Move the subtitle files to the video directories
    print()
    print("Move the subtitle files to the video directories & Rename the subtitle files...")
    
    # print language options
    print("Language Options:")
    print("\t0. No specific language(empty)")
    for i, lang in enumerate(SUBTITLE_LANGUAGES):
        print("\t%d. %s" % (i+1, lang))

    # select language
    lang_selection = input("Step 4. Please select the language for the subtitle files: ")
    clear_screen()
    if lang_selection.isdigit() and int(lang_selection) >= 0 and int(lang_selection) <= len(SUBTITLE_LANGUAGES):
        if int(lang_selection) != 0:
            selected_lang = "." + list(SUBTITLE_LANGUAGES)[int(lang_selection)-1]
        else:
            selected_lang = ""

    # show operation details
    print()
    print("Selected Language: [%s]" % selected_lang)
    print("Operation Details: ")

    for relation in matched_relations:
        video_dir = os.path.dirname(relation.video.path)
        subtitle_dir = os.path.dirname(relation.subtitle.path)
        subtitle_name = os.path.basename(relation.subtitle.path)

        # Rename the subtitle file
        new_subtitle_name = os.path.splitext(relation.video.name)[0] + selected_lang + os.path.splitext(relation.subtitle.name)[1]
        new_subtitle_path = os.path.join(video_dir, new_subtitle_name)

        print("\tMove: %s" % relation.subtitle.path)
        print("\t  ==> %s" % new_subtitle_path)

    # Confirm the operation
    confirm = input("Step 5. Do you want to proceed with the operation? (Y/N)")
    if confirm.lower() != 'y':
        print("Operation Cancelled.")
        exit()

    clear_screen()
    print ("Operation in Progress...")

    # Move and Rename the subtitle files
    for relation in matched_relations:
        video_dir = os.path.dirname(relation.video.path)
        subtitle_dir = os.path.dirname(relation.subtitle.path)
        subtitle_name = os.path.basename(relation.subtitle.path)

        # Rename the subtitle file
        new_subtitle_name = os.path.splitext(relation.video.name)[0] + selected_lang + os.path.splitext(relation.subtitle.name)[1]
        new_subtitle_path = os.path.join(video_dir, new_subtitle_name)

        os.rename(relation.subtitle.path, new_subtitle_path)
        print("\tMoved: %s" % relation.subtitle.path)
        print("\t   ==> %s" % new_subtitle_path)

    print("Operation Completed!")

    

# Usage
# python neatsub.py
# 1. Enter the directory which contains the [video] files
# 2. Enter the directory which contains the [subtitle] files
#   2-1. If there are multiple [subtitle extensions], you can select what you want to keep

# 3. Try to match the video files with the subtitle files
#   3-1. If not all files are matched, you can [ignore the show name] and try to match the rest of the files(by season and episode)

# 4. Select the language for the subtitle files, which corresponds to the language suffix in the emby/jellyfin (e.g., .zh-CN.srt, .en.srt)

# 5. Preview the operation details and confirm the operation 
