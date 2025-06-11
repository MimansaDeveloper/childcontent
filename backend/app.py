from flask import Flask, request, render_template, jsonify
import os
from werkzeug.utils import secure_filename
import uuid

from color_score_analysis import analyze_color
from camera_movement_analysis import analyze_motion
from flash_score_analysis import analyze_flash_effects
from density_score_analysis import analyze_object_density
from scene_change_analysis import analyze_scene_change

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'video' not in request.files:
        return "No file part", 400

    file = request.files['video']
    if file.filename == '':
        return "No selected file", 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        print("\n📁 File uploaded successfully.")
        print("🔍 Starting video analysis...")

        print("▶️ Step 1: Color Saturation and Brightness Analysis")
        color_score = analyze_color(filepath)

        print("▶️ Step 2: Camera Motion Analysis")
        motion_score = analyze_motion(filepath)

        print("▶️ Step 3: Flashing Effects Detection")
        flash_score = analyze_flash_effects(filepath)

        print("▶️ Step 4: On-screen Object/Character Density")
        object_score = analyze_object_density(filepath)

        print("▶️ Step 5: Scene Change Frequency")
        scene_score = analyze_scene_change(filepath)

        print("✅ All features analyzed.")

        # Combine into final score
        scores = [color_score, motion_score, flash_score, object_score, scene_score]
        final_score = round(sum(scores) / len(scores), 2)

        print(f"\n📊 Final Combined Score: {final_score}")

        return jsonify({
            "Color Score": color_score,
            "Motion Score": motion_score,
            "Flash Score": flash_score,
            "Object Density Score": object_score,
            "Scene Change Score": scene_score,
            "Final Score": final_score
        })
    else:
        return "Invalid file type", 400

if __name__ == '__main__':
    app.run(debug=True)