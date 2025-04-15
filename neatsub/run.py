from flask import Flask, request, jsonify, send_from_directory
import os
import logging
from werkzeug.utils import secure_filename
from neatsub import process_subtitle_file
from config_manager import ConfigManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')

# Initialize ConfigManager
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
config_manager = ConfigManager(CONFIG_FILE)

# Ensure temp directory exists
os.makedirs(config_manager.temp_dir, exist_ok=True)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_subtitle():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Get parameters from request
    lang_suffix = request.form.get('lang_suffix', '')  # Empty string by default
    overwrite = request.form.get('overwrite', '').lower() == 'true'  # False by default

    # Print parameters
    logger.info(f"Lang suffix: {lang_suffix}")
    logger.info(f"Overwrite: {overwrite}")

    if file:
        filename = secure_filename(file.filename)
        logger.info(f"Uploading file: {filename}")
        allowed_extensions = set()
        # Add both subtitle and subtitle pack extensions
        for ext in config_manager.subtitle_extensions + config_manager.subtitle_pack_extensions:
            allowed_extensions.add(ext[1:])  # Remove the dot from extension

        if not allowed_file(filename, allowed_extensions):
            return jsonify({'error': 'File type not allowed'}), 400

        # Save file to temp directory
        temp_path = os.path.join(config_manager.temp_dir, filename)
        file.save(temp_path)

        try:
            # Process the subtitle file with new parameters
            results = process_subtitle_file(temp_path, config_manager, lang_suffix=lang_suffix, overwrite=overwrite)
            return jsonify({
                'message': 'File processed successfully',
                'results': results
            })
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return jsonify({'error': str(e)}), 500

@app.route("/config", methods=["GET"])
def get_config():
    return jsonify({
        "video_file_extensions": config_manager.video_extensions,
        "subtitle_file_extensions": config_manager.subtitle_extensions,
        "subtitle_pack_extensions": config_manager.subtitle_pack_extensions,
        "temp_dir": config_manager.temp_dir,
        "media_libraries": config_manager.media_libraries
    })

@app.route("/config", methods=["POST"])
def update_config():
    data = request.json

    # Check if all fields are valid
    for field in ["video_file_extensions", "subtitle_file_extensions", "subtitle_pack_extensions", "media_libraries"]:
        if not isinstance(data[field], list):
            return jsonify({'error': f'Invalid {field}'}), 400
    
    if not isinstance(data["temp_dir"], str):
        return jsonify({'error': 'Invalid temp_dir'}), 400

    try:
        config_manager.video_extensions = data["video_file_extensions"]
        config_manager.subtitle_extensions = data["subtitle_file_extensions"]
        config_manager.subtitle_pack_extensions = data["subtitle_pack_extensions"]
        config_manager.temp_dir = data["temp_dir"]
        config_manager.media_libraries = data["media_libraries"]
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Config updated successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
