import cv2
import numpy as np

def flash_score(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return 0

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30

    ret, prev_frame = cap.read()
    if not ret:
        print("Couldn't read the first frame.")
        return 0

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    sudden_change_count = 0

    for _ in range(1, frame_count):
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray, prev_gray)
        change = np.sum(diff > 50) / diff.size  # % of pixels with significant brightness change

        if change > 0.4:  # More than 40% pixels change = flash
            sudden_change_count += 1

        prev_gray = gray

    cap.release()

    duration_minutes = frame_count / fps / 60
    flashes_per_min = sudden_change_count / duration_minutes if duration_minutes > 0 else 0

    # Scoring: 2 flashes/min = score 1, 20 flashes/min = score 10
    min_flash = 2
    max_flash = 20
    normalized = (flashes_per_min - min_flash) / (max_flash - min_flash)
    normalized = max(0, min(normalized, 1))  # Clamp between 0 and 1
    flash_score = 1 + 9 * (normalized ** 0.5)

    return flash_score