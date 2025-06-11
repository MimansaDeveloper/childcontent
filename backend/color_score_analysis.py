import cv2
import numpy as np

def color_score(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0
    sat_scores = []
    val_scores = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        s = hsv[:, :, 1].mean()
        v = hsv[:, :, 2].mean()
        sat_scores.append(s)
        val_scores.append(v)
    cap.release()
    avg_sat = np.mean(sat_scores)
    avg_val = np.mean(val_scores)
    sat_norm = (avg_sat - 50) / (150 - 50)
    val_norm = (avg_val - 70) / (250 - 70)
    sat_norm = np.clip(sat_norm, 0, 1)
    val_norm = np.clip(val_norm, 0, 1)
    combined = (sat_norm + val_norm) / 2
    return 1 + 9 * combined