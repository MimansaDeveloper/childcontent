import cv2
import argparse
from datetime import timedelta
import time
import signal
import sys

# Set up argument parsing
parser = argparse.ArgumentParser(description="Detects scene changes in a video or live stream and optionally writes timestamps to a text file.")
parser.add_argument("--input", help="Path to the input video file or URL of the live stream.", required=True)
parser.add_argument("--textout", help="Enable text output to a file and specify the file path.", nargs='?', const="scene_changes.txt", type=str)
parser.add_argument("--silent", help="Run in background without video window. Faster performance.", action="store_true")
parser.add_argument("--verbose", help="Enable verbose output showing progress and FPS.", action="store_true")
parser.add_argument("--threshold", help="Threshold for histogram correlation (lower = more sensitive). Default: 0.98", type=float, default=0.98)
parser.add_argument("--min-interval", help="Minimum interval (in seconds) between two scene changes. Default: 1s", type=float, default=1.0)

args = parser.parse_args()

VIDEO_SOURCE = args.input
TEXTOUT_FILE = args.textout if args.textout is not None else None
SILENT_MODE = args.silent
VERBOSE_MODE = args.verbose
HIST_THRESHOLD = args.threshold
MIN_INTERVAL = args.min_interval

# Global variables
cap = None
file_out = None
overlay_timeout = 25
frame_counter = 0
overlay_active = False
scene_change_count = 0  # Counter for scene changes

# Signal handler
def signal_handler(signum, frame):
    print("\nReceived termination signal. Exiting gracefully...")
    if cap:
        cap.release()
    if file_out:
        file_out.close()
    cv2.destroyAllWindows()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Load video or stream
cap = cv2.VideoCapture(VIDEO_SOURCE)
if not cap.isOpened():
    print(f"Error opening video source: {VIDEO_SOURCE}")
    sys.exit(1)

try:
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
except ValueError:
    total_frames = -1

current_frame = 0

# Open output file if enabled
if TEXTOUT_FILE:
    file_out = open(TEXTOUT_FILE, "w")

# Overlay helper
def draw_overlay(frame, text="Scene Change Detected"):
    cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

try:
    incoming_data, frame = cap.read()
    if not incoming_data:
        print("Error reading the first frame from the video.")
        sys.exit(1)

    previous_histogram = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    previous_histogram = cv2.normalize(previous_histogram, previous_histogram).flatten()

    last_scene_change = 0
    start_time = time.time()

    while True:
        incoming_data, frame = cap.read()
        if not incoming_data:
            if total_frames > 0:
                break  # EOF for video file
            else:
                time.sleep(1)
                continue  # Live stream fallback

        current_frame += 1
        histogram = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        histogram = cv2.normalize(histogram, histogram).flatten()

        d = cv2.compareHist(previous_histogram, histogram, cv2.HISTCMP_CORREL)
        current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

        if d < HIST_THRESHOLD and (current_time - last_scene_change >= MIN_INTERVAL or last_scene_change == 0):
            time_stamp = timedelta(seconds=current_time)
            formatted_time = str(time_stamp)
            scene_change_count += 1
            if file_out:
                file_out.write(f"Scene change at: {formatted_time}\n")
            if not SILENT_MODE:
                draw_overlay(frame)
                overlay_active = True
                frame_counter = 0
            last_scene_change = current_time

        if not SILENT_MODE:
            if overlay_active and frame_counter < overlay_timeout:
                draw_overlay(frame)
                frame_counter += 1
            else:
                overlay_active = False

        if VERBOSE_MODE:
            fps = current_frame / (time.time() - start_time)
            if total_frames > 0:
                progress = int(50 * current_frame / total_frames)
                bar = "[" + "=" * progress + " " * (50 - progress) + "]"
                print(f"\r{bar} {current_frame}/{total_frames} frames, FPS: {fps:.2f}", end="")
            else:
                print(f"\r{current_frame} frames processed, FPS: {fps:.2f}", end="")

        previous_histogram = histogram

        if not SILENT_MODE:
            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

finally:
    if cap:
        cap.release()
    if file_out:
        file_out.close()
    cv2.destroyAllWindows()
    if current_time > 0:
        minutes = current_time / 60.0
        avg_changes_per_min = scene_change_count / minutes
        print(f"\nTotal scene changes: {scene_change_count}")
        print(f"Video duration: {current_time:.2f} seconds ({minutes:.2f} minutes)")
        print(f"Average scene changes per minute: {avg_changes_per_min:.2f}")
        lower_bound = 4
        upper_bound = 21.96
        score = 1 + (avg_changes_per_min - lower_bound) * (9 / (upper_bound - lower_bound))
        score = max(1, min(score, 10))  # Clamp between 1 and 10
        print(f"Scene change activity score (1-10): {score:.2f}")
    else:
        print(f"\nTotal scene changes detected: {scene_change_count} (Live stream or zero duration video)")
