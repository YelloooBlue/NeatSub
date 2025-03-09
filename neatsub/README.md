# Usage

### 1. Install Requirement
`pip install -r requirements.txt`
### 2. Configuration
1. Create a `config.json` file in the same folder as `run.py`
2. Configure `temp_dir` field as a temporary address for **storing uploaded files** (after subtitles are processed, the files will be deleted)
3. Configure `library_name`, `library_path` field as your media library (you can add more)
    ```json
    {
        "version": "1.0",
        "video_file_extensions": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"],
        "subtitle_file_extensions": [".srt", ".ass", ".ssa"],
        "subtitle_pack_extensions": [".zip", ".rar", ".7z"],
        "temp_dir": ".tmp",
        "media_libraries": [
            {
                "library_name": "The US tvshow",
                "library_path": "media/media_library"
            }
        ]
    }
    ```
### 3. Run
`python run.py`
### 4. Visit the website
`http://127.0.0.1:5000` (depends on your output)

### 5. Upload your Subtitle File or Subtitle Pack
(The guide picture is coming soon...)


