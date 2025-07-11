from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import uuid
import traceback
import time
from concurrent.futures import ThreadPoolExecutor
import requests
import yt_dlp
import csv

# --- Analysis Modules ---
from scene_change_analysis import scene_change_score
from flash_score_analysis import flash_score
from camera_movement_analysis import camera_movement_score
from color_score_analysis import color_score
from density_score_analysis import density_score
from animation_analysis import animation_transition_score
from expression_analysis import facial_expression_intensity_score
from fantastical_content_analysis import fantastical_content_score
from narrative_coherence_analysis import narrative_coherence_score
from audio_overwhelm_analysis import audio_overwhelm_score
from speech_rate_analysis import speech_rate_score

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Max 100MB file
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        print("\n🔔 Received POST /analyze")
        start_total = time.time()

        video = None
        filepath = None
        filename = None

        if 'video' in request.files:
            video = request.files['video']
            print(f"📄 File name: {video.filename}")
            video_bytes = video.read()
            print(f"📦 File size: {round(len(video_bytes) / 1024 / 1024, 2)} MB")
            video.seek(0)

            filename = str(uuid.uuid4()) + os.path.splitext(video.filename)[1]
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            video.save(filepath)
            print(f"✅ Video uploaded and saved to: {filepath}")

        elif 'video_url' in request.form:
            video_url = request.form['video_url'].strip()
            if not video_url.lower().startswith('http'):
                return jsonify({'error': 'Invalid URL'}), 400

            print(f"🌐 Downloading from URL: {video_url}")
            ext = '.mp4'
            filename = str(uuid.uuid4()) + ext
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            if 'youtube.com' in video_url or 'youtu.be' in video_url:
                print("📽️ Using yt_dlp for YouTube download...")
                try:
                    ydl_opts = {
                        'format': 'best[ext=mp4]',
                        'outtmpl': filepath,
                        'quiet': True,
                        'noplaylist': True
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                    print(f"✅ YouTube video saved to: {filepath}")
                except Exception as e:
                    print("❌ yt_dlp error:", str(e))
                    return jsonify({'error': 'Failed to download YouTube video'}), 500
            else:
                print("🔽 Downloading non-YouTube video with requests...")
                try:
                    r = requests.get(video_url, stream=True, timeout=30)
                    r.raise_for_status()
                    with open(filepath, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"✅ Video downloaded and saved to: {filepath}")
                except Exception as e:
                    print("❌ Error downloading video:", str(e))
                    return jsonify({'error': 'Failed to download video from URL'}), 500
        else:
            print("❌ No video input found")
            return jsonify({'error': 'No video or video_url provided'}), 400

        print("📋 Starting parallel analysis...\n")
        timings = {}

        def timed(name, func):
            print(f"⏳ [{name}] started...")
            t0 = time.time()
            result = func(filepath)
            duration = round(time.time() - t0, 2)
            timings[name] = duration
            print(f"✅ [{name}] completed in {duration}s → Score: {result}")
            return float(result)

        with ThreadPoolExecutor() as executor:
            futures = {
                'scene': executor.submit(timed, 'Scene Change', scene_change_score),
                'camera': executor.submit(timed, 'Camera Movement', camera_movement_score),
                'flash': executor.submit(timed, 'Flashing Effects', flash_score),
                'color': executor.submit(timed, 'Color Score', color_score),
                'density': executor.submit(timed, 'Object Density', density_score),
                'animation': executor.submit(timed, 'Animation', animation_transition_score),
                'expression': executor.submit(timed, 'Facial Expression Intensity', facial_expression_intensity_score),
                'fancy': executor.submit(timed, 'Fantastical Content', fantastical_content_score),
                'narrative': executor.submit(timed, 'Narrative Coherence', narrative_coherence_score),
                'audio': executor.submit(timed, 'Audio Overwhelm', audio_overwhelm_score),
                'speech_rate': executor.submit(timed, 'Speech Rate', speech_rate_score)
            }

            scores = {k: future.result() for k, future in futures.items()}

        final_score = round(sum(scores.values()) / len(scores), 2)
        total_time = round(time.time() - start_total, 2)

        print("\n📊 Summary:")
        for name, sec in timings.items():
            print(f"• {name} took {sec} seconds")
        print(f"🎯 Final Score: {final_score}")
        print(f"🕒 Total Time: {total_time} seconds\n")

        return jsonify({
            'filename': filename,
            'scene_change': scores['scene'],
            'camera_movement': scores['camera'],
            'flashing_effects': scores['flash'],
            'color': scores['color'],
            'object_density': scores['density'],
            'animation': scores['animation'],
            'facial_expression_intensity': scores['expression'],
            'fantastical_content': scores['fancy'],
            'narrative_coherence': scores['narrative'],
            'audio_overwhelm': scores['audio'],
            'speech_rate': scores['speech_rate'],
            'final_score': final_score
        })

    except Exception as e:
        print("❌ Error occurred during analysis:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.json
        video_name = data.get('video_name', 'unknown')
        rating = data.get('rating', '')
        comments = data.get('comments', '')

        with open("feedback.csv", mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([video_name, rating, comments])

        print(f"✅ Feedback recorded for {video_name}")
        return jsonify({"status": "success"})

    except Exception as e:
        print("❌ Error saving feedback:", str(e))
        return jsonify({"error": "Failed to save feedback"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
