import cv2
import numpy as np
import argparse
from tqdm import tqdm
import os
import warnings
warnings.filterwarnings("ignore")

def compute_flash_score(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30

    ret, prev_frame = cap.read()
    if not ret:
        print("Couldn't read the first frame.")
        return

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    sudden_change_count = 0

    for _ in tqdm(range(1, frame_count), desc="Analyzing frames"):
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray, prev_gray)
        change = np.sum(diff > 50) / diff.size  # Percentage of significant pixel change

        # Consider it a flash if more than 40% of pixels change significantly
        if change > 0.4:
            sudden_change_count += 1

        prev_gray = gray

    cap.release()

    duration = frame_count / fps / 60  # in minutes
    flashes_per_min = sudden_change_count / duration if duration > 0 else 0

    print(f"\nTotal sudden visual changes (flashes): {sudden_change_count}")
    print(f"Average flashes per minute: {flashes_per_min:.2f}")

    # Scoring: 2 flashes/min = 1, 20 flashes/min = 10
    min_flash = 2
    max_flash = 20
    normalized = (flashes_per_min - min_flash) / (max_flash - min_flash)
    normalized = max(0, min(normalized, 1))
    flash_score = 1 + 9 * (normalized ** 0.5)
    print(f"Flashing Effects Score (1–10): {flash_score:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze flashing effects in a video.")
    parser.add_argument("--input", required=True, help="Path to input video file")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print("File does not exist.")
    else:
        compute_flash_score(args.input)
