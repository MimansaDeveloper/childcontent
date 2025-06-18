import cv2
import numpy as np

# Load Haar Cascade classifiers for face, eyes, and mouth
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
mouth_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')  # Best available for mouth/smile

def facial_expression_intensity_score(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return 1

    intense_count = 0
    total_faces = 0
    frame_interval = 5  # Analyze every 5th frame
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % frame_interval == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60))

            for (x, y, w, h) in faces:
                total_faces += 1
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]

                # Detect eyes and mouth within face ROI
                eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=8, minSize=(15, 15))
                mouths = mouth_cascade.detectMultiScale(roi_gray, scaleFactor=1.5, minNeighbors=15, minSize=(20, 20))

                # Use bounding box size as proxy for expression exaggeration
                eye_intensity = sum([(ew * eh) / (w * h) for (_, _, ew, eh) in eyes])
                mouth_intensity = sum([(mw * mh) / (w * h) for (_, _, mw, mh) in mouths])

                expression_score = eye_intensity + mouth_intensity
                if expression_score > 0.08:  # Tuned empirically
                    intense_count += 1

        frame_id += 1

    cap.release()

    if total_faces == 0:
        return 1

    intensity_ratio = intense_count / total_faces

    # Scoring: 0.1 = score 1, 0.6+ = score 10
    lower_bound = 0.10
    upper_bound = 0.19
    score = 1 + (intensity_ratio - lower_bound) * (9 / (upper_bound - lower_bound))
    score = max(1, min(score, 10))
    return score

