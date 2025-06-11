import cv2
import numpy as np
import argparse
from tqdm import tqdm
import os
import warnings
warnings.filterwarnings("ignore")

def compute_object_density_score(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30

    fgbg = cv2.createBackgroundSubtractorMOG2()
    motion_pixel_ratios = []

    for _ in tqdm(range(frame_count), desc="Processing frames"):
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

    avg_density = np.mean(motion_pixel_ratios)
    print(f"\nAverage moving object density: {avg_density:.4f}")

    # Scoring system:
    # 0.01 (very low) = score 1, 0.2 (high) = score 10
    min_density = 0.01
    max_density = 0.2
    normalized = (avg_density - min_density) / (max_density - min_density)
    normalized = max(0, min(normalized, 1))
    density_score = 1 + 9 * (normalized ** 0.6)

    print(f"Object/Character Density Score (1–10): {density_score:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze on-screen object/character density in a video.")
    parser.add_argument("--input", required=True, help="Path to input video file")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print("File does not exist.")
    else:
        compute_object_density_score(args.input)
