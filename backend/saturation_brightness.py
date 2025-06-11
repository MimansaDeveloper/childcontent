import cv2
import numpy as np
import argparse

def compute_scores(avg_saturation, avg_brightness):
    # Saturation: 50 → 1, 150 → 10
    sat_min, sat_max = 50, 150
    saturation_score = 1 + ((avg_saturation - sat_min) * 9 / (sat_max - sat_min))
    saturation_score = np.clip(saturation_score, 1, 10)

    # Brightness: 70 → 1, 250 → 10
    bright_min, bright_max = 70, 250
    brightness_score = 1 + ((avg_brightness - bright_min) * 9 / (bright_max - bright_min))
    brightness_score = np.clip(brightness_score, 1, 10)

    return saturation_score, brightness_score

def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video: {video_path}")
        return

    total_saturation = 0
    total_brightness = 0
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1]
        brightness = hsv[:, :, 2]

        total_saturation += np.mean(saturation)
        total_brightness += np.mean(brightness)
        frame_count += 1

    cap.release()

    if frame_count == 0:
        print("No frames analyzed.")
        return

    avg_saturation = total_saturation / frame_count
    avg_brightness = total_brightness / frame_count

    sat_score, bright_score = compute_scores(avg_saturation, avg_brightness)
    color_rating = 0.5 * sat_score + 0.5 * bright_score  # Weighted average

    print(f"\n--- Color & Brightness Analysis ---")
    print(f"Average Saturation: {avg_saturation:.2f}")
    print(f"Average Brightness: {avg_brightness:.2f}")
    print(f"Saturation Score (1–10): {sat_score:.2f}")
    print(f"Brightness Score (1–10): {bright_score:.2f}")
    print(f"Final Color Rating (1–10): {color_rating:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze color saturation and brightness of a video.")
    parser.add_argument("--input", required=True, help="Path to input video file.")
    args = parser.parse_args()
    analyze_video(args.input)
