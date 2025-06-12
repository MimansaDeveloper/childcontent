import cv2
import numpy as np

def scene_change_score(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return 0

    scene_change_count = 0
    threshold = 0.98  # Histogram correlation threshold
    min_interval = 1.0  # Minimum seconds between scene changes

    ret, frame = cap.read()
    if not ret:
        print("Error reading the first frame.")
        return 0

    prev_hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8],
                             [0, 256, 0, 256, 0, 256])
    prev_hist = cv2.normalize(prev_hist, prev_hist).flatten()

    last_change_time = 0
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_index = 1
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8],
                            [0, 256, 0, 256, 0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        corr = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)

        current_time = frame_index / fps

        if corr < threshold and (current_time - last_change_time >= min_interval or last_change_time == 0):
            scene_change_count += 1
            last_change_time = current_time

        prev_hist = hist
        frame_index += 1

    cap.release()

    duration_sec = total_frames / fps
    if duration_sec <= 0:
        print("Zero duration video or live stream.")
        return 1

    changes_per_min = scene_change_count / (duration_sec / 60)

    # Scoring: 4 = 1, 21.96 = 10
    lower_bound = 4
    upper_bound = 21.96
    score = 1 + (changes_per_min - lower_bound) * (9 / (upper_bound - lower_bound))
    score = max(1, min(score, 10))  # Clamp score between 1 and 10
    return score