import cv2
import numpy as np
import argparse
from tqdm import tqdm

# Argument parser
parser = argparse.ArgumentParser(description="Analyze camera movement frequency in a video.")
parser.add_argument("--input", required=True, help="Path to the input video file.")
parser.add_argument("--resize", type=float, default=0.5, help="Resize factor for frames (0.5 = half size).")
parser.add_argument("--skip", type=int, default=1, help="Number of frames to skip (1 = no skip, 2 = every 2nd frame, etc.)")
args = parser.parse_args()

# Open video
cap = cv2.VideoCapture(args.input)
if not cap.isOpened():
    print(f"Error opening video file: {args.input}")
    exit(1)

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Optical flow params
prev_gray = None
total_magnitude = 0
frame_count = 0

# Progress bar
pbar = tqdm(total=total_frames, desc="Analyzing Camera Movement", unit="frame")

frame_idx = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_idx += 1
    pbar.update(1)

    # Skip frames for speed
    if frame_idx % args.skip != 0:
        continue

    # Resize for faster processing
    frame_resized = cv2.resize(frame, (0, 0), fx=args.resize, fy=args.resize)
    gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

    if prev_gray is not None:
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, gray,
            None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        avg_magnitude = np.mean(magnitude)
        total_magnitude += avg_magnitude
        frame_count += 1

    prev_gray = gray

pbar.close()
cap.release()

if frame_count > 0:
    avg_motion = total_magnitude / frame_count
    print(f"\nAverage camera motion magnitude: {avg_motion:.4f}")

    # Scoring using nonlinear scaling
    min_motion = 0.5
    max_motion = 5.0
    normalized = (avg_motion - min_motion) / (max_motion - min_motion)
    normalized = max(0, normalized)
    motion_score = 1 + 9 * (normalized ** 0.26)
    motion_score = max(1, min(10, motion_score))  # Clamp
    print(f"Camera Movement Score (1–10): {motion_score:.2f}")
else:
    print("Not enough frames to analyze.")
