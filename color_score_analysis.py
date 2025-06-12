import cv2
import numpy as np

def color_score(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video: {video_path}")
        return 0

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
        return 0

    avg_saturation = total_saturation / frame_count
    avg_brightness = total_brightness / frame_count

    # Compute saturation score
    sat_min, sat_max = 50, 150
    sat_score = 1 + ((avg_saturation - sat_min) * 9 / (sat_max - sat_min))
    sat_score = np.clip(sat_score, 1, 10)

    # Compute brightness score
    bright_min, bright_max = 70, 250
    bright_score = 1 + ((avg_brightness - bright_min) * 9 / (bright_max - bright_min))
    bright_score = np.clip(bright_score, 1, 10)

    # Combine
    final_score = 0.5 * sat_score + 0.5 * bright_score

    return final_score
