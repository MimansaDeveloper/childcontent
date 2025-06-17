import whisper
from moviepy.editor import VideoFileClip
import os
import tempfile

def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, verbose=False, logger=None)

def speech_rate_score(video_path):
    model = whisper.load_model("base")
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
        extract_audio(video_path, tmp_audio.name)
        audio_path = tmp_audio.name

    result = model.transcribe(audio_path)
    os.remove(audio_path)

    transcript = result["text"]
    duration = result["segments"][-1]["end"] if result["segments"] else 1
    word_count = len(transcript.strip().split())
    duration_minutes = duration / 60.0

    if duration_minutes == 0:
        return 1.0  # Avoid division by zero

    wpm = word_count / duration_minutes
    print(f"Estimated Words Per Minute (WPM): {wpm:.2f}")

    # Scoring system: 90 WPM = 1, 210 WPM = 10
    min_wpm, max_wpm = 90, 210
    normalized = (wpm - min_wpm) / (max_wpm - min_wpm)
    normalized = max(0, min(normalized, 1))
    score = 1 + 9 * normalized
    print(f"Speech Rate Score (1–10): {score:.2f}")
    return score

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Analyze speech rate in a video.")
    parser.add_argument("--input", required=True, help="Path to input video file")
    args = parser.parse_args()

    if os.path.exists(args.input):
        speech_rate_score(args.input)
    else:
        print("File does not exist.")
