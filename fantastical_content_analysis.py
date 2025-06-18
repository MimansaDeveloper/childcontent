import cv2
import numpy as np
from moviepy.editor import VideoFileClip

def fantastical_content_score(video_path):
    cap = cv2.VideoCapture(video_path)
    prev_gray = None
    total_frames = 0
    fantastical_motion = 0
    bright_magic_colors = 0
    low_edge_scenes = 0

    # Define HSV ranges for common "fantasy" colors
    lower_pink = np.array([140, 100, 100])
    upper_pink = np.array([170, 255, 255])
    
    lower_green = np.array([40, 70, 70])
    upper_green = np.array([80, 255, 255])

    lower_blue = np.array([90, 60, 60])
    upper_blue = np.array([130, 255, 255])

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        total_frames += 1

        frame = cv2.resize(frame, (320, 180))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Count pixels in magic/fantasy-like color ranges
        pink_mask = cv2.inRange(hsv, lower_pink, upper_pink)
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        color_score = (
            np.count_nonzero(pink_mask) +
            np.count_nonzero(green_mask) +
            np.count_nonzero(blue_mask)
        ) / (frame.shape[0] * frame.shape[1])

        if color_score > 0.15:
            bright_magic_colors += 1

        # Unrealistic motion (high optical flow magnitude)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is not None:
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
            )
            magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            if np.mean(magnitude) > 4:  # Arbitrary threshold for fast motion
                fantastical_motion += 1
        prev_gray = gray

        # Low edge content → less realistic settings
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.count_nonzero(edges) / (edges.shape[0] * edges.shape[1])
        if edge_density < 0.02:
            low_edge_scenes += 1

    cap.release()

    if total_frames == 0:
        return 1.0

    # Combine the three metrics (normalized)
    magic_color_ratio = bright_magic_colors / total_frames
    motion_ratio = fantastical_motion / total_frames
    edge_ratio = low_edge_scenes / total_frames

    raw_score = (magic_color_ratio + motion_ratio + edge_ratio) / 3  # [0, 1]

    # Map 0.1 → 1, 0.19+ → 10
    if raw_score <= 0.1:
        final_score = 1
    elif raw_score >= 0.19:
        final_score = 10
    else:
        final_score = 1 + ((raw_score - 0.1) / (0.09)) * 9

    return final_score

