import cv2
import numpy as np

def density_score(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0
    bg_subtractor = cv2.createBackgroundSubtractorMOG2()
    density_values = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        fg_mask = bg_subtractor.apply(frame)
        count = np.sum(fg_mask > 0)
        density_values.append(count)
    cap.release()
    avg_density = np.mean(density_values)
    normalized = np.clip(avg_density / 100000, 0, 1)
    return 1 + 9 * normalized