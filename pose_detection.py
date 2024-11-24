# pose_detection.py

import cv2
import mediapipe as mp
import time
import logging
import configparser
import sys
import os
from database import Database

def process_video(video_path, output_path, db_config, config, position_name=None):
    """
    Process the video for pose detection and log data to the database.

    Args:
        video_path (str): Path to the input video file.
        output_path (str): Path to save the output video file.
        db_config (dict): Database configuration parameters.
        config (dict): Additional configuration parameters.
        position_name (str): Name of the BJJ position or technique.
    """
    try:
        scale_factor = config.getfloat('scale_factor', fallback=0.5)
        skip_rate = config.getint('skip_rate', fallback=1)
        batch_size = config.getint('batch_size', fallback=100)
        log_file = config.get('log_file', 'app.log')

        # Use the existing logger
        logger = logging.getLogger()

        logger.info("Starting video processing.")

        # Initialize MediaPipe Pose
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,           # Lightest model for fastest processing
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        mp_drawing = mp.solutions.drawing_utils

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Error opening video file {video_path}")
            raise FileNotFoundError(f"Cannot open video file: {video_path}")

        # Get video properties
        frame_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps          = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        logger.info(f"Input video FPS: {fps}")
        frame_duration = 1 / fps
        logger.info(f"Frame duration based on FPS: {frame_duration:.4f} seconds")

        # Reduce frame resolution
        frame_width = int(frame_width * scale_factor)
        frame_height = int(frame_height * scale_factor)

        # Define the codec and create VideoWriter object
        out = cv2.VideoWriter(
            output_path,
            cv2.VideoWriter_fourcc(*'mp4v'),
            fps,
            (frame_width, frame_height)
        )

        # Initialize database
        db = Database(db_config)
        db.create_tables()

        # Initialize counters
        processed_frames = 0
        frame_counter = 0

        # Batch for database inserts
        batch_data = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_counter += 1

            # Skip frames if necessary
            if frame_counter % skip_rate != 0:
                # Optionally, write the original frame without processing
                out.write(frame)
                continue

            start_time_proc = time.time()

            # Resize frame to reduce processing time
            frame = cv2.resize(frame, (frame_width, frame_height))

            # Convert the BGR frame to RGB for processing
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the image and find pose landmarks
            results = pose.process(image_rgb)

            # Draw the pose annotation on the original frame
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame,                      # Image to draw on
                    results.pose_landmarks,     # Pose landmarks
                    mp_pose.POSE_CONNECTIONS,   # Connections between landmarks
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),  # Landmarks style
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)                    # Connections style
                )

                # Collect pose data for batch insert
                frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                data_to_insert = []
                for idx, landmark in enumerate(results.pose_landmarks.landmark):
                    data = {
                        'frame': frame_number,
                        'landmark_id': idx,
                        'x': landmark.x,
                        'y': landmark.y,
                        'visibility': landmark.visibility
                    }
                    if position_name:
                        data['position_name'] = position_name
                    data_to_insert.append(data)
                batch_data.extend(data_to_insert)

                # Insert batch data when batch size is reached
                if len(batch_data) >= batch_size:
                    db.insert_pose_data(batch_data)
                    batch_data = []

            # Write the frame to the output video
            out.write(frame)
            processed_frames += 1

            end_time_proc = time.time()
            processing_time = end_time_proc - start_time_proc
            logger.info(f"Frame {processed_frames}/{total_frames}, Processing time: {processing_time:.4f} seconds")

            # Check if processing time exceeds frame duration
            if processing_time > frame_duration:
                logger.warning("Processing time exceeds frame duration. Synchronization issues may occur.")

        # Insert any remaining data
        if batch_data:
            db.insert_pose_data(batch_data)

        # Release resources
        cap.release()
        out.release()
        pose.close()
        db.close()

        logger.info(f"Processing complete. Output saved to '{output_path}'")
        logger.info(f"Total frames: {total_frames}, Processed frames: {processed_frames}")

    except Exception as e:
        logger.exception("An error occurred during video processing.")
        sys.exit(1)

    if __name__ == '__main__':
        # Read configuration
        config = configparser.ConfigParser()
        config.read('config.ini')
        default_config = config['DEFAULT']

        # Define db_config
        db_config = {
            'db_type': config.get('DATABASE', 'db_type', fallback='postgres'),
            'db_host': config.get('DATABASE', 'db_host', fallback='db'),
            'db_port': config.get('DATABASE', 'db_port', fallback='5432'),
            'db_user': config.get('DATABASE', 'db_user', fallback='user'),
            'db_password': config.get('DATABASE', 'db_password', fallback='password'),
            'db_name': config.get('DATABASE', 'db_name', fallback='pose_db'),
        }

        # Define input and output paths
        video_path = default_config.get('video_path', 'uploads/default_video.mp4')
        output_path = default_config.get('output_path', 'outputs/processed_video.mp4')

        # Call the process_video function
        process_video(
            video_path=video_path,
            output_path=output_path,
            db_config=db_config,
            config=config,
            position_name=None  # No position name in this context
        )
