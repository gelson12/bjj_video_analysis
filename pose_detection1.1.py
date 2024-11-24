# pose_detection.py

import cv2
import mediapipe as mp
import time

# Initialize MediaPipe Pose with lighter model
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,           # Reduced complexity for faster processing
    enable_segmentation=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

def process_video(video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file {video_path}")
        return

    # Get video properties
    frame_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps          = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Input video FPS: {fps}")
    frame_duration = 1 / fps
    print(f"Frame duration based on FPS: {frame_duration:.4f} seconds")

    # Define the codec and create VideoWriter object
    out = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*'mp4v'),  # Try 'avc1' if issues persist
        fps,
        (frame_width, frame_height)
    )

    processed_frames = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        start_time = time.time()

        # Optional: Resize frame to reduce processing time
        # scale_factor = 0.5
        # frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
        # frame_height, frame_width = frame.shape[:2]

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

        # Write the frame to the output video
        out.write(frame)
        processed_frames += 1

        end_time = time.time()
        processing_time = end_time - start_time
        print(f"Frame {processed_frames}/{total_frames}, Processing time: {processing_time:.4f} seconds")

        # Check if processing time exceeds frame duration
        if processing_time > frame_duration:
            print("Warning: Processing time exceeds frame duration. Synchronization issues may occur.")

    # Release resources
    cap.release()
    out.release()
    pose.close()

    print(f"Processing complete. Output saved to '{output_path}'")
    print(f"Total frames: {total_frames}, Processed frames: {processed_frames}")

if __name__ == '__main__':
    video_path = 'gopro_20231009_p_3209896140992833444_1_3209896140992833444.mp4'  # Replace with your video file
    output_path = 'output_video.mp4'
    process_video(video_path, output_path)
