# app.py

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import uuid
import traceback

# --- Analysis modules (commented for now) ---
# from scene_change_analysis import scene_change_score
# from flash_score_analysis import flash_score
# from camera_movement_analysis import camera_movement_score
# from color_score_analysis import color_score
# from density_score_analysis import density_score

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        print("🔔 POST /analyze triggered")
        print("📦 Request content type:", request.content_type)
        print("📁 Uploaded files:", request.files)

        if 'video' not in request.files:
            print("❌ No video part in request.files")
            return jsonify({'error': 'No video file uploaded'}), 400

        video = request.files['video']
        print("📄 Received file:", video.filename)

        # Check file size
        video_bytes = video.read()
        print(f"📦 File size: {len(video_bytes)} bytes")
        video.seek(0)

        filename = str(uuid.uuid4()) + os.path.splitext(video.filename)[1]
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video.save(filepath)

        print("✅ File saved to:", filepath)

        # ------- Uncomment below once upload works fully --------
        # print("🔍 Starting analysis...")
        # scene_score = float(scene_change_score(filepath))
        # print("📊 Scene score:", scene_score)

        # camera_score = float(camera_movement_score(filepath))
        # print("📊 Camera score:", camera_score)

        # flash_scor = float(flash_score(filepath))
        # print("📊 Flash score:", flash_scor)

        # color_scor = float(color_score(filepath))
        # print("📊 Color score:", color_scor)

        # density_scor = float(density_score(filepath))
        # print("📊 Density score:", density_scor)

        # final_score = round((scene_score + camera_score + flash_scor + color_scor + density_scor) / 5, 2)

        # return jsonify({
        #     'scene_change': scene_score,
        #     'camera_movement': camera_score,
        #     'flashing_effects': flash_scor,
        #     'color': color_scor,
        #     'object_density': density_scor,
        #     'final_score': final_score
        # })

        # ✅ Temporary test return
        return jsonify({"status": "✅ File uploaded successfully", "filename": filename})

    except Exception as e:
        print("❌ Exception occurred:", e)
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT env var
    app.run(host='0.0.0.0', port=port)
