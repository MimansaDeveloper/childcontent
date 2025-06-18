import cv2
import numpy as np

def camera_movement_score(video_path, resize_factor=0.4, frame_skip=3):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return 0

    total_magnitude = 0
    frame_count = 0
    prev_gray = None
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1
        if frame_idx % frame_skip != 0:
            continue

        try:
            frame_small = cv2.resize(frame, (0, 0), fx=resize_factor, fy=resize_factor)
            gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
        except Exception as e:
            print(f"Skipping frame {frame_idx} due to error: {e}")
            continue

        if prev_gray is not None:
            # Use Farneback optical flow
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, gray,
                None, 0.5, 3, 15, 3, 5, 1.2, 0
            )
            magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            total_magnitude += np.mean(magnitude)
            frame_count += 1

        prev_gray = gray

    cap.release()

    if frame_count == 0:
        print("Not enough frames to analyze.")
        return 0

    avg_motion = total_magnitude / frame_count

    # Non-linear scaling for score
    min_motion = 0.5
    max_motion = 5.0
    normalized = max(0, (avg_motion - min_motion) / (max_motion - min_motion))
    motion_score = 1 + 9 * (normalized ** 0.26)
    return max(1, min(10, motion_score))  # Clamp to 1–10
