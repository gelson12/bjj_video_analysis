# app.py

from flask import Flask, request, jsonify
import os
import configparser
import logging
from pose_detection import process_video
from video_processor import process_video_segment

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Read configuration
config = configparser.ConfigParser()
config.read('config.ini')
default_config = config['DEFAULT']

# Define db_config
db_config = {
    'db_type': config.get('DATABASE', 'db_type', fallback='sqlite'),
    'db_host': config.get('DATABASE', 'db_host', fallback='db'),  # 'db' is the service name in docker-compose
    'db_port': config.get('DATABASE', 'db_port', fallback='5432'),
    'db_user': config.get('DATABASE', 'db_user', fallback='user'),
    'db_password': config.get('DATABASE', 'db_password', fallback='password'),
    'db_name': config.get('DATABASE', 'db_name', fallback='pose_db'),
}

# Configure logging with exception handling
try:
    log_file = default_config.get('log_file', 'app.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
except Exception as e:
    print(f"Failed to configure logging to file '{log_file}': {e}")
    # Fallback to console logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def parse_time_string(time_str):
    """
    Parses a time string in 'hh:mm:ss', 'mm:ss', or 'ss' format and returns total seconds.
    """
    try:
        parts = [float(part) for part in time_str.strip().split(':')]
        if len(parts) == 3:
            hours, minutes, seconds = parts
            total_seconds = hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            minutes, seconds = parts
            total_seconds = minutes * 60 + seconds
        elif len(parts) == 1:
            total_seconds = parts[0]
        else:
            raise ValueError("Invalid time format")
        return total_seconds
    except ValueError as e:
        logging.exception(f"Invalid time format: {time_str}")
        raise ValueError(f"Invalid time format: {time_str}") from e

@app.route('/upload', methods=['POST'])
def upload_video():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file:
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            output_path = os.path.join(OUTPUT_FOLDER, f"processed_{filename}")
            file.save(filepath)
            process_video(
                video_path=filepath,
                output_path=output_path,
                db_config=db_config,
                config=default_config,
                position_name=None  # No position name for local uploads
            )
            return jsonify({'message': 'Video processed successfully', 'output_video': output_path}), 200
    except Exception as e:
        logging.exception("An error occurred during video upload and processing.")
        return jsonify({'error': str(e)}), 500

@app.route('/process_video', methods=['POST'])
def process_youtube_video():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Invalid JSON data'}), 400

        video_url = data.get('video_url')
        position_name = data.get('position_name')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if not all([video_url, position_name, start_time, end_time]):
            return jsonify({'error': 'Missing required parameters'}), 400

        # Parse time strings if they are strings
        if isinstance(start_time, str):
            start_time = parse_time_string(start_time)
        if isinstance(end_time, str):
            end_time = parse_time_string(end_time)

        # Validate time ranges
        if not (0 <= start_time < end_time):
            return jsonify({'error': 'Invalid time range: start_time must be less than end_time and non-negative'}), 400

        output_path = process_video_segment(
            video_url=video_url,
            start_time=start_time,
            end_time=end_time,
            position_name=position_name,
            db_config=db_config,
            config=default_config
        )

        return jsonify({'message': 'Video processed successfully', 'output_video': output_path}), 200
    except ValueError as ve:
        logging.exception("A value error occurred during YouTube video processing.")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logging.exception("An error occurred during YouTube video processing.")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
