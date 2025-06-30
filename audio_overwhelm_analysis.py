import numpy as np
import os
import tempfile
import subprocess
from scipy.signal import bilinear, lfilter
from scipy.io import wavfile


def a_weighting(fs):
    f1 = 20.598997
    f2 = 107.65265
    f3 = 737.86223
    f4 = 12194.217
    A1000 = 1.9997

    nums = [(2 * np.pi * f4)**2 * (10 ** (A1000 / 20)), 0, 0, 0, 0]
    dens = np.convolve([1, 4 * np.pi * f4, (2 * np.pi * f4)**2],
                       [1, 4 * np.pi * f1, (2 * np.pi * f1)**2])
    dens = np.convolve(np.convolve(dens, [1, 2 * np.pi * f3]), [1, 2 * np.pi * f2])

    b, a = bilinear(nums, dens, fs)
    return b, a


def compute_a_weighted_rms(signal, fs=16000):
    b, a = a_weighting(fs)
    weighted = lfilter(b, a, signal)
    return float(np.sqrt(np.mean(weighted ** 2)))


def rms_to_db(rms):
    return 20 * np.log10(rms + 1e-10)


def audio_overwhelm_score(video_path, chunk_duration=1.0):
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.wav")

        # Extract audio using ffmpeg
        command = [
            "ffmpeg", "-i", video_path,
            "-ac", "1", "-ar", "16000",  # Mono, 16kHz
            "-loglevel", "quiet",
            audio_path
        ]
        subprocess.run(command, check=True)

        fs, data = wavfile.read(audio_path)
        if data.ndim > 1:
            data = data.mean(axis=1)

        # Normalize
        data = data / np.max(np.abs(data))

        chunk_size = int(fs * chunk_duration)
        loudness_values = []

        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            if len(chunk) < chunk_size:
                break
            rms = compute_a_weighted_rms(chunk, fs)
            db = rms_to_db(rms)
            loudness_values.append(db)

        if len(loudness_values) < 2:
            print("⚠️ Not enough audio chunks for analysis.")
            return 1

        loudness_values = np.array(loudness_values)
        avg_loudness = np.mean(loudness_values)
        std_loudness = np.std(loudness_values)
        sudden_peaks = np.sum(np.diff(loudness_values) > 8)  # abrupt jumps
        high_volume_bursts = np.sum(loudness_values > -15)  # many loud moments

        # Normalized features (0 to 1)
        loud_penalty = min(1.0, (avg_loudness + 25) / 20)  # -25 dB to -5 dB
        variability_penalty = min(1.0, std_loudness / 10)
        peak_penalty = min(1.0, sudden_peaks / 10)
        burst_penalty = min(1.0, high_volume_bursts / len(loudness_values))

        overwhelm_score = (loud_penalty + variability_penalty + peak_penalty + burst_penalty) / 4
        final_score = 1 + 9 * overwhelm_score

        return final_score

