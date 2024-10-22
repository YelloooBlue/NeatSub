# NeatSub
NeatSub is an intelligent subtitle file management tool designed to streamline the workflow for video content creators and enthusiasts. This powerful yet intuitive software addresses a common challenge: how to quickly and efficiently match and rename large numbers of subtitle files with their corresponding video files.

# ToDo
- A Package may contain enforce subtitles，CC subtitles, etc. 

  (may be distinguished by the file size)
- A Package may contain multiple languages of subtitles

# Usage

```python neatsub.py```
1. Enter the directory which contains the [video] files
2. Enter the directory which contains the [subtitle] files

   2-1. If there are multiple [subtitle extensions], you can select what you want to keep

3. Try to match the video files with the subtitle files
   
   3-1. If not all files are matched, you can [ignore the show name] and try to match the rest of the files(by season and episode)

4. Select the language for the subtitle files
   
   which corresponds to the language suffix in the emby/jellyfin (e.g., .zh-CN.srt, .en.srt)

5. Preview the operation details and confirm the operation
