import os
import numpy as np
import tempfile
import ffmpeg
import soundfile as sf
import pyloudnorm as pyln
from ffmpeg._run import Error as FFmpegError  # Correct import

def extract_audio_ffmpeg(input_path, output_path):
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, ac=1, ar=16000, format='wav')
            .overwrite_output()
            .run(quiet=True)
        )
    except FFmpegError as e:
        print("❌ FFmpeg error:", e.stderr.decode() if e.stderr else "No stderr.")
        raise

def compute_chunk_loudness(audio_data, sample_rate, chunk_size):
    """
    Analyze audio in chunks of chunk_size seconds and compute loudness values
    """
    meter = pyln.Meter(sample_rate)
    chunk_samples = int(chunk_size * sample_rate)
    loudness_values = []

    for i in range(0, len(audio_data), chunk_samples):
        chunk = audio_data[i:i + chunk_samples]
        if len(chunk) < chunk_samples:
            continue
        try:
            loudness = meter.integrated_loudness(chunk)
            if np.isfinite(loudness):
                loudness_values.append(loudness)
        except Exception as e:
            print(f"⚠️ Skipping chunk {i // chunk_samples}: {e}")
            continue

    return np.array(loudness_values)

def audio_overwhelm_score(video_path, chunk_duration=1.0):
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.wav")

        # Extract audio using ffmpeg-python
        extract_audio_ffmpeg(video_path, audio_path)

        # Load audio
        data, rate = sf.read(audio_path)
        if data.ndim > 1:
            data = np.mean(data, axis=1)

        if len(data) == 0 or np.all(data == 0):
            print("⚠️ Audio data is empty or silent.")
            return 1.0

        # Compute overall LUFS
        meter = pyln.Meter(rate)
        try:
            lufs = meter.integrated_loudness(data)
        except Exception as e:
            print("⚠️ Could not compute LUFS:", e)
            return 1.0

        # Analyze loudness over chunks
        loudness_chunks = compute_chunk_loudness(data, rate, chunk_duration)
        loudness_chunks = loudness_chunks[np.isfinite(loudness_chunks)]  # Remove NaN, inf

        if len(loudness_chunks) < 2:
            print("⚠️ Not enough valid audio chunks for analysis.")
            return 1.0

        std_loudness = np.std(loudness_chunks)
        peaks = np.sum(np.abs(np.diff(loudness_chunks)) > 5)
        high_volume_bursts = np.sum(loudness_chunks > -15)

        # Scoring (normalize to 0–1)
        base_penalty = min(1.0, (-lufs - 10) / 20)  # -30 to -10 LUFS
        variation_penalty = min(1.0, std_loudness / 6)
        peak_penalty = min(1.0, peaks / 10)
        burst_penalty = min(1.0, high_volume_bursts / len(loudness_chunks))

        final_penalty = (base_penalty + variation_penalty + peak_penalty + burst_penalty) / 4
        final_score = 1 + 9 * final_penalty

        return final_score
