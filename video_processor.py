# video_processor.py

import os
import yt_dlp
import logging
from pose_detection import process_video

def process_video_segment(video_url, start_time, end_time, position_name, db_config, config):
    """
    Downloads a segment of a YouTube video and processes it.

    Args:
        video_url (str): The URL of the YouTube video.
        start_time (float): Start time of the segment in seconds.
        end_time (float): End time of the segment in seconds.
        position_name (str): Name of the BJJ position or technique.
        db_config (dict): Database configuration parameters.
        config (dict): Additional configuration parameters.

    Returns:
        str: Path to the processed output video.
    """
    try:
        downloads_dir = 'downloads'
        os.makedirs(downloads_dir, exist_ok=True)
        output_filename = f"temp_video_{os.getpid()}.mp4"
        video_filepath = os.path.join(downloads_dir, output_filename)

        # Configure yt_dlp logger to use the application's logger
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
            'outtmpl': video_filepath,
            'download_sections': [  # Correctly use a list
                {
                    'section': 'video',  # Optional: name the section
                    'start_time': start_time,
                    'end_time': end_time,
                }
            ],
            'logger': YTLogger(),
            'verbose': True,  # Enable verbose logging
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logging.info(f"Downloading video segment from {video_url}")
            ydl.download([video_url])

        # Verify that the video was downloaded
        if not os.path.exists(video_filepath) or os.path.getsize(video_filepath) == 0:
            logging.error(f"Failed to download video segment from {video_url}")
            raise FileNotFoundError(f"Downloaded video file is missing or empty: {video_filepath}")

        # Define output path
        outputs_dir = 'outputs'
        os.makedirs(outputs_dir, exist_ok=True)
        output_filename = f"processed_{os.path.basename(video_filepath)}"
        output_path = os.path.join(outputs_dir, output_filename)

        # Process the video segment
        process_video(
            video_path=video_filepath,
            output_path=output_path,
            db_config=db_config,
            config=config,
            position_name=position_name
        )

        # Clean up temporary files
        if os.path.exists(video_filepath):
            os.remove(video_filepath)

        return output_path
    except Exception as e:
        logging.exception("An error occurred during video segment processing.")
        raise e
