import os
import asyncio
from deepgram import Deepgram
import numpy as np

DEEPGRAM_API_KEY = "api key"  # Replace this

def map_speech_rate_to_score(wpm: float) -> float:
    """
    Converts words-per-minute to overstimulation score.
    - <100 WPM: calm (score near 1)
    - 180+ WPM: overwhelming (score near 10)
    """
    if wpm < 100:
        return 1
    elif wpm > 180:
        return 10
    else:
        return round(1 + 9 * ((wpm - 100) / 80) ** 0.6, 2)


async def transcribe_with_deepgram(video_path: str):
    dg_client = Deepgram(DEEPGRAM_API_KEY)

    with open(video_path, "rb") as audio:
        source = {'buffer': audio, 'mimetype': 'video/mp4'}
        options = {'punctuate': True, 'utterances': True}

        response = await dg_client.transcription.prerecorded(source, options)

        words = response['results']['channels'][0]['alternatives'][0]['words']
        return words


def calculate_wpm(words, start_time, end_time):
    total_words = len(words)
    duration_minutes = (end_time - start_time) / 60
    if duration_minutes == 0:
        return 0
    return total_words / duration_minutes


def speech_rate_score(video_path: str) -> float:
    """Computes the speech rate score from video using Deepgram transcript."""
    words = asyncio.run(transcribe_with_deepgram(video_path))

    if not words or len(words) < 2:
        print("Not enough words to compute speech rate.")
        return 1.0

    timestamps = [w['start'] for w in words if 'start' in w]
    if not timestamps:
        return 1.0

    start_time = timestamps[0]
    end_time = max(w.get('end', 0) for w in words)
    duration_minutes = (end_time - start_time) / 60.0
    if duration_minutes <= 0:
        return 1.0

    wpm = len(words) / duration_minutes
    print(f"Words per minute: {wpm:.2f}")

    # Map 5 WPM → 1 and 90 WPM → 10 (clamped)
    min_wpm = 5
    max_wpm = 90
    normalized = (wpm - min_wpm) / (max_wpm - min_wpm)
    normalized = max(0, min(1, normalized))  # Clamp to [0, 1]
    score = 1 + 9 * normalized
    return score


