import cv2
import numpy as np

def fantastical_content_score(video_path, frame_stride=5):
    cap = cv2.VideoCapture(video_path)
    prev_gray = None
    total_frames = 0
    bright_magic_colors = 0
    fantastical_motion = 0
    low_edge_scenes = 0
    frame_idx = 0

    # Predefine magic color ranges (in HSV)
    lower_pink, upper_pink = np.array([140, 100, 100]), np.array([170, 255, 255])
    lower_green, upper_green = np.array([40, 70, 70]), np.array([80, 255, 255])
    lower_blue, upper_blue = np.array([90, 60, 60]), np.array([130, 255, 255])

    frame_width, frame_height = 320, 180
    frame_area = frame_width * frame_height

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1
        if frame_idx % frame_stride != 0:
            continue

        total_frames += 1
        frame = cv2.resize(frame, (frame_width, frame_height))

        # --- Color mask analysis ---
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        color_mask = (
            cv2.inRange(hsv, lower_pink, upper_pink) |
            cv2.inRange(hsv, lower_green, upper_green) |
            cv2.inRange(hsv, lower_blue, upper_blue)
        )
        color_ratio = np.count_nonzero(color_mask) / frame_area
        if color_ratio > 0.15:
            bright_magic_colors += 1

        # --- Unrealistic motion (optical flow) ---
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is not None:
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, gray, None, 0.5, 1, 12, 3, 5, 1.1, 0
            )
            mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            if np.mean(mag) > 4:
                fantastical_motion += 1
        prev_gray = gray

        # --- Edge density analysis ---
        edges = cv2.Canny(gray, 100, 200)
        edge_ratio = np.count_nonzero(edges) / frame_area
        if edge_ratio < 0.02:
            low_edge_scenes += 1

    cap.release()

    if total_frames == 0:
        return 1.0

    # Normalize and average
    magic_color_ratio = bright_magic_colors / total_frames
    motion_ratio = fantastical_motion / total_frames
    edge_ratio = low_edge_scenes / total_frames
    raw_score = (magic_color_ratio + motion_ratio + edge_ratio) / 3

    # Map score range
    if raw_score <= 0.1:
        final_score = 1
    elif raw_score >= 0.19:
        final_score = 10
    else:
        final_score = 1 + ((raw_score - 0.1) / 0.09) * 9

    return final_score
