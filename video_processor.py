# video_processor.py

import os
import yt_dlp
import logging
import subprocess
from pose_detection import process_video

def download_full_video(video_url, download_path, cookies_path=None):
    class YTLogger(object):
        def debug(self, msg):
            logging.debug(msg)

        def info(self, msg):
            logging.info(msg)

        def warning(self, msg):
            logging.warning(msg)

        def error(self, msg):
            logging.error(msg)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': download_path,
        'logger': YTLogger(),
        'verbose': True,
    }

    if cookies_path and os.path.exists(cookies_path):
        ydl_opts['cookiefile'] = cookies_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        logging.info(f"Downloading full video from {video_url}")
        ydl.download([video_url])

    if not os.path.exists(download_path) or os.path.getsize(download_path) == 0:
        logging.error(f"Failed to download video from {video_url}")
        raise FileNotFoundError(f"Downloaded video file is missing or empty: {download_path}")

def trim_video(input_path, output_path, start_time, end_time):
    trim_command = [
        'ffmpeg',
        '-i', input_path,
        '-ss', str(start_time),
        '-to', str(end_time),
        '-c', 'copy',
        output_path,
        '-y'  # Overwrite without asking
    ]

    logging.info(f"Trimming video segment: {output_path}")
    subprocess.run(trim_command, check=True)

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        logging.error(f"Failed to trim video segment: {output_path}")
        raise FileNotFoundError(f"Trimmed video file is missing or empty: {output_path}")

def process_video_segment(video_url, start_time, end_time, position_name, db_config, config, cookies_path=None):
    try:
        downloads_dir = 'downloads'
        os.makedirs(downloads_dir, exist_ok=True)
        full_video_filename = f"full_video_{os.getpid()}.mp4"
        full_video_filepath = os.path.join(downloads_dir, full_video_filename)

        # Download the full video with cookies (if provided)
        download_full_video(video_url, full_video_filepath, cookies_path)

        # Define trimmed video path
        trimmed_video_filename = f"trimmed_video_{os.getpid()}.mp4"
        trimmed_video_filepath = os.path.join(downloads_dir, trimmed_video_filename)

        # Trim the video segment
        trim_video(full_video_filepath, trimmed_video_filepath, start_time, end_time)

        # Define output path
        outputs_dir = 'outputs'
        os.makedirs(outputs_dir, exist_ok=True)
        output_filename = f"processed_{os.path.basename(trimmed_video_filepath)}"
        output_path = os.path.join(outputs_dir, output_filename)

        # Process the trimmed video segment
        process_video(
            video_path=trimmed_video_filepath,
            output_path=output_path,
            db_config=db_config,
            config=config,
            position_name=position_name
        )

        # Clean up temporary files
        for file in [full_video_filepath, trimmed_video_filepath]:
            if os.path.exists(file):
                os.remove(file)

        return output_path
    except subprocess.CalledProcessError as e:
        logging.exception("ffmpeg failed to trim the video.")
        raise e
    except Exception as e:
        logging.exception("An error occurred during video segment processing.")
        raise e
