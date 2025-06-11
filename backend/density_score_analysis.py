import cv2
import numpy as np

def density_score(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return 0

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fgbg = cv2.createBackgroundSubtractorMOG2()
    motion_pixel_ratios = []

    for _ in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fgmask = fgbg.apply(gray)

        motion_pixels = np.sum(fgmask > 127)
        total_pixels = fgmask.size
        motion_ratio = motion_pixels / total_pixels
        motion_pixel_ratios.append(motion_ratio)

    cap.release()

    if not motion_pixel_ratios:
        return 0

    avg_density = np.mean(motion_pixel_ratios)

    # Scoring: 0.01 (low) = 1, 0.2 (high) = 10
    min_density = 0.01
    max_density = 0.2
    normalized = (avg_density - min_density) / (max_density - min_density)
    normalized = max(0, min(normalized, 1))  # Clamp between 0 and 1

    density_score = 1 + 9 * (normalized ** 0.6)

    return density_score