# Usage

## Docker

1. Pull the image and run the container
    Replace `YOUR_MEDIA_LIBRARY_PATH` with your actual media library path
    ```bash
    docker run -d -p 8095:8095 --name=NeatSub --restart=always -v YOUR_MEDIA_LIBRARY_PATH:/media yelloooblue/neatsub:latest
    ```
1. Visit the website
    `http://127.0.0.1:8095` (depends on your server IP and port mapping)
2. Setup your media library in the web UI
    - Click the "Settings" button on the bottom right corner
    - Add your media library name and path (like `/media/tvshow` if you followed the above example)
3. Upload your Subtitle File or Subtitle Pack
    (The guide picture is coming soon...)

## Python

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


