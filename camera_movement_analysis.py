import cv2
import numpy as np

def camera_movement_score(video_path, resize_factor=0.5, frame_skip=1):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return 0

    total_magnitude = 0
    frame_count = 0
    frame_idx = 0
    prev_gray = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1
        if frame_idx % frame_skip != 0:
            continue

        try:
            frame_resized = cv2.resize(frame, (0, 0), fx=resize_factor, fy=resize_factor)
            gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        except Exception as e:
            print(f"Skipping frame {frame_idx} due to error: {e}")
            continue

        if prev_gray is not None:
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, gray,
                None, 0.5, 3, 15, 3, 5, 1.2, 0
            )
            magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            avg_magnitude = np.mean(magnitude)
            total_magnitude += avg_magnitude
            frame_count += 1

        prev_gray = gray

    cap.release()

    if frame_count == 0:
        print("Not enough frames to analyze.")
        return 0

    avg_motion = total_magnitude / frame_count

    # Scoring using nonlinear scaling
    min_motion = 0.5
    max_motion = 5.0
    normalized = (avg_motion - min_motion) / (max_motion - min_motion)
    normalized = max(0, normalized)
    motion_score = 1 + 9 * (normalized ** 0.26)
    motion_score = max(1, min(10, motion_score))  # Clamp

    return motion_score
