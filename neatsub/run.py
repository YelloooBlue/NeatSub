from flask import Flask, request, jsonify
import os
import json
from werkzeug.utils import secure_filename
import logging
from neatsub import process_subtitle_file

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

CONFIG_FILE = '/Users/lanhuang/Documents/Projects/NeatSub/neatsub/config.json'

# Load configuration
def load_config():
    try:
        with open(CONFIG_FILE , 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        return None

config = load_config()

# Ensure temp directory exists
os.makedirs(config['temp_dir'], exist_ok=True)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

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
    logger.debug(f"Lang suffix: {lang_suffix}")
    logger.debug(f"Overwrite: {overwrite}")

    if file:
        filename = secure_filename(file.filename)
        allowed_extensions = set()
        # Add both subtitle and subtitle pack extensions
        for ext in config['subtitle_file_extensions'] + config['subtitle_pack_extensions']:
            allowed_extensions.add(ext[1:])  # Remove the dot from extension

        if not allowed_file(filename, allowed_extensions):
            return jsonify({'error': 'File type not allowed'}), 400

        # Save file to temp directory
        temp_path = os.path.join(config['temp_dir'], filename)
        file.save(temp_path)

        try:
            # Process the subtitle file with new parameters
            results = process_subtitle_file(temp_path, config, lang_suffix=lang_suffix, overwrite=overwrite)
            return jsonify({
                'message': 'File processed successfully',
                'results': results
            })
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
