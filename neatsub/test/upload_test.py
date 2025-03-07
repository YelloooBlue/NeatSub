"""
    Upload test
"""

import unittest
import os
import requests
import json
from pathlib import Path
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global configuration - modify these values directly
CONFIG = {
    'server_url': 'http://localhost:5000/upload',
    'test_data_dir': '/Users/lanhuang/Documents/Projects/NeatSub/neatsub/test/test_data/subtitle_files',
    'lang_suffix': '*',
    'overwrite': True
}

class TestUpload(unittest.TestCase):
    """Test uploading subtitle files to local Flask server"""
    
    def setUp(self):
        """Set up test data"""
        self.test_dir = Path(CONFIG['test_data_dir'])
        self.server_url = CONFIG['server_url']
        
        # Ensure test directory exists
        if not self.test_dir.exists():
            raise FileNotFoundError(f"Test subtitle directory not found: {self.test_dir}")

    def _upload_file(self, file_path: Path, lang_suffix: str = "", overwrite: bool = False) -> dict:
        """Helper method to upload a single file with parameters"""
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f)}
            data = {}
            if lang_suffix:
                data['lang_suffix'] = lang_suffix
            if overwrite:
                data['overwrite'] = 'true'
                
            try:
                response = requests.post(self.server_url, files=files, data=data)
                response.raise_for_status()
                
                result = {
                    'filename': file_path.name,
                    'status': response.status_code,
                    'response': response.json()
                }
                logger.info(f"Successfully uploaded {file_path.name}")
                logger.info(f"Server response: {json.dumps(response.json(), indent=2)}")
                return result
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to upload {file_path.name}: {str(e)}")
                return {
                    'filename': file_path.name,
                    'status': 'error',
                    'error': str(e)
                }

    def test_upload_files(self):
        """Test uploading all subtitle files in the test directory"""
        # Get all subtitle files
        subtitle_files = []
        for ext in ['.srt', '.ass', '.ssa', '.sub', '.idx']:
            subtitle_files.extend(self.test_dir.glob(f'*{ext}'))
        
        if not subtitle_files:
            logger.warning("No subtitle files found in test directory")
            return
            
        logger.info(f"Found {len(subtitle_files)} subtitle files to upload")
        
        # Upload each file and collect results
        results = []
        for file_path in subtitle_files:
            result = self._upload_file(
                file_path, 
                lang_suffix=CONFIG['lang_suffix'],
                overwrite=CONFIG['overwrite']
            )
            results.append(result)
            
            # Add a small delay between uploads
            time.sleep(0.5)
        
        # Print summary
        logger.info("\nUpload Summary:")
        logger.info(f"Total files: {len(subtitle_files)}")
        
        # Check both HTTP status and results field
        true_success_count = 0
        http_success_count = 0
        
        for r in results:
            if r['status'] == 200:
                http_success_count += 1
                # Check if results field is not empty
                if r['response'].get('results') and len(r['response']['results']) > 0:
                    true_success_count += 1
                else:
                    logger.warning(f"File {r['filename']} uploaded but no video matches found")
        
        logger.info(f"HTTP successful uploads: {http_success_count}")
        logger.info(f"True matches (with video): {true_success_count}")
        logger.info(f"Failed uploads: {len(subtitle_files) - http_success_count}")
        logger.info(f"Uploads without matches: {http_success_count - true_success_count}")
        
        # Assert overall success rate for true matches
        self.assertGreater(true_success_count / len(subtitle_files), 0.5)  # At least 50% true match rate

if __name__ == '__main__':
    unittest.main()

