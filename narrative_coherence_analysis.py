import cv2
import numpy as np

def narrative_coherence_score(video_path, threshold=30.0, resize_factor=0.5):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return 1  # Safe fallback

    prev_frame = None
    frame_idx = 0
    fps = cap.get(cv2.CAP_PROP_FPS) or 30  # Default to 30 if unknown
    scene_times = []

    last_scene_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1
        frame_small = cv2.resize(frame, (0, 0), fx=resize_factor, fy=resize_factor)
        gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)

        if prev_frame is not None:
            diff = cv2.absdiff(gray, prev_frame)
            score = np.mean(diff)
            if score > threshold:
                # Scene change detected
                time_sec = frame_idx / fps
                duration = time_sec - last_scene_time
                scene_times.append(duration)
                last_scene_time = time_sec

        prev_frame = gray

    cap.release()

    if len(scene_times) < 2:
        print("Not enough scenes detected for narrative coherence analysis.")
        return 1

    avg_duration = np.mean(scene_times)
    std_duration = np.std(scene_times)

    # High std deviation + short average scene duration = incoherent
    variability_penalty = min(1.0, std_duration / avg_duration)  # normalize
    short_scene_penalty = min(1.0, (2.0 - avg_duration) / 2.0) if avg_duration < 2.0 else 0

    incoherence_level = (variability_penalty + short_scene_penalty) / 2

    # Map to score: higher incoherence → higher score
    final_score = 1 + 9 * incoherence_level
    return final_score