import cv2
import numpy as np

def animation_transition_score(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return 0

    abrupt_change_count = 0
    diff_threshold = 45  # Pixel intensity difference threshold
    min_interval = 1.0  # Minimum seconds between abrupt transitions

    ret, prev_frame = cap.read()
    if not ret:
        print("Error reading the first frame.")
        return 0

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    last_change_time = 0
    frame_index = 1
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev_gray, gray)
        mean_diff = np.mean(diff)

        current_time = frame_index / fps
        if mean_diff > diff_threshold and (current_time - last_change_time >= min_interval or last_change_time == 0):
            abrupt_change_count += 1
            last_change_time = current_time

        prev_gray = gray
        frame_index += 1

    cap.release()

    duration_sec = total_frames / fps
    if duration_sec <= 0:
        print("Zero duration video or live stream.")
        return 1

    changes_per_min = abrupt_change_count / (duration_sec / 60)

    # Scoring: 2 = 1, 20 = 10
    lower_bound = 2
    upper_bound = 20
    score = 1 + (changes_per_min - lower_bound) * (9 / (upper_bound - lower_bound))
    score = max(1, min(score, 10))
    return score
