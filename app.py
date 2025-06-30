from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import uuid
import traceback
import time
from concurrent.futures import ThreadPoolExecutor

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

        if 'video' not in request.files:
            print("❌ No video file found in request")
            return jsonify({'error': 'No video file uploaded'}), 400

        video = request.files['video']
        print(f"📄 File name: {video.filename}")
        video_bytes = video.read()
        print(f"📦 File size: {round(len(video_bytes) / 1024 / 1024, 2)} MB")
        video.seek(0)

        # Save file
        filename = str(uuid.uuid4()) + os.path.splitext(video.filename)[1]
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video.save(filepath)
        print(f"✅ Video saved to: {filepath}")

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

        # Run in parallel
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
                'audio': executor.submit(timed, 'Audio Overwhelm', audio_overwhelm_score)

            }

            scene_score = futures['scene'].result()
            camera_score = futures['camera'].result()
            flash_scor = futures['flash'].result()
            color_scor = futures['color'].result()
            density_scor = futures['density'].result()
            animation_scor = futures['animation'].result()
            expression_scor = futures['expression'].result()
            fantastical_scor = futures['fancy'].result()
            narrative_scor = futures['narrative'].result()
            audio_scor = futures['audio'].result()



        final_score = round((scene_score + camera_score + flash_scor + color_scor +
                     density_scor + animation_scor + expression_scor +
                     fantastical_scor + narrative_scor + audio_scor) / 10, 2)



        total_time = round(time.time() - start_total, 2)

        print("\n📊 Summary:")
        for name, sec in timings.items():
            print(f"• {name} took {sec} seconds")
        print(f"🎯 Final Score: {final_score}")
        print(f"🕒 Total Time: {total_time} seconds\n")

        return jsonify({
            'scene_change': scene_score,
            'camera_movement': camera_score,
            'flashing_effects': flash_scor,
            'color': color_scor,
            'object_density': density_scor,
            'animation': animation_scor,
            'facial_expression_intensity': expression_scor,
            'fantastical_content': fantastical_scor,
            'narrative_coherence': narrative_scor,
            'audio_overwhelm': audio_scor,
            'final_score': final_score
        })

    except Exception as e:
        print("❌ Error occurred during analysis:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
