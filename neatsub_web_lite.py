#
# Author: YelloooBlue
# Date: 2024-12-02
#

'''
    Receive a GET request with Tvshow_Path 
    and then get all subtitle files in the folder
    Finally, rename the subtitle files and add suffix to them
'''
import flask
import neatsub



# ==================================

app = flask.Flask(__name__)

@app.route('/do', methods=['GET'])
def do():
    tvshow_path = flask.request.args.get('Tvshow_Path')
    if not tvshow_path:
        return 'Tvshow_Path is required', 400

    if not os.path.exists(tvshow_path):
        return 'Tvshow_Path does not exist', 400
    
    # Scan Video files
    video_files = neatsub.scan_video_files(tvshow_path)
    if not video_files:
        return 'No video files found', 400
    
    # Scan subtitle files
    subtitle_files = neatsub.scan_subtitle_files(tvshow_path)
    if not subtitle_files:
        return 'No subtitle files found', 400

    # Scan video files
