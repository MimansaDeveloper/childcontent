import cv2
import numpy as np

def camera_movement_score(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0
    ret, prev = cap.read()
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    magnitudes = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        magnitudes.append(np.mean(mag))
        prev_gray = gray
    cap.release()
    avg_motion = np.mean(magnitudes)
    normalized = np.clip(avg_motion / 0.5, 0, 1)
    score = 1 + 9 * (normalized ** 0.26)
    return min(10, max(1, score))