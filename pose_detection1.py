import cv2
import mediapipe as mp
import os
import logging

# Suppress TensorFlow and absl logging if desired
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow INFO and WARNING messages
logging.getLogger('tensorflow').setLevel(logging.FATAL)

# Initialize MediaPipe Pose.
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Initialize drawing utility
mp_drawing = mp.solutions.drawing_utils

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file {video_path}")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the BGR frame to RGB.
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Process the image and find pose landmarks.
        results = pose.process(image)

        # Draw the pose annotation on the image.
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Display the resulting frame.
        cv2.imshow('MediaPipe Pose', frame)

        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # Replace 'path_to_your_video.mp4' with the actual path to your video file
    video_path = 'gopro_20231009_p_3209896140992833444_1_3209896140992833444.mp4'
    process_video(video_path)
