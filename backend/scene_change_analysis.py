import cv2
import numpy as np
import sys

def scene_change_score(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0

    _, prev = cap.read()
    prev_hist = cv2.calcHist([prev], [0], None, [256], [0, 256])
    prev_hist = cv2.normalize(prev_hist, prev_hist).flatten()
    scene_changes = 0
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        curr_hist = cv2.calcHist([frame], [0], None, [256], [0, 256])
        curr_hist = cv2.normalize(curr_hist, curr_hist).flatten()
        diff = cv2.compareHist(prev_hist, curr_hist, cv2.HISTCMP_CORREL)
        if diff < 0.92:
            scene_changes += 1
        prev_hist = curr_hist
        frame_count += 1

    cap.release()
    duration_sec = frame_count / fps
    changes_per_min = scene_changes / (duration_sec / 60)
    score = 1 + 9 * ((changes_per_min - 4) / (21.96 - 4))
    return max(1, min(score, 10))