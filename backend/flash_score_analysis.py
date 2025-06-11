import cv2
import numpy as np

def flash_score(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0
    last_brightness = None
    flash_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        curr_brightness = np.mean(gray)
        if last_brightness is not None:
            diff = abs(curr_brightness - last_brightness)
            if diff > 40:
                flash_count += 1
        last_brightness = curr_brightness
    cap.release()
    flashes_per_min = flash_count / (cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS) / 60)
    return min(10, max(1, flashes_per_min / 10 * 9 + 1))