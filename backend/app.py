# app.py (Backend for Video Analysis)

from flask import Flask, request, jsonify, render_template
import os
import uuid
from scene_change_analysis import scene_change_score
from flash_score_analysis import flash_score
from camera_movement_analysis import camera_movement_score
from color_score_analysis import color_score
from density_score_analysis import density_score

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file uploaded'}), 400

    video = request.files['video']
    filename = str(uuid.uuid4()) + os.path.splitext(video.filename)[1]
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    video.save(filepath)

    print("Video uploaded and saved at:", filepath)

    print("Starting analysis...")
    scene_score = scene_change_score(filepath)
    print("Scene score:", scene_score)

    camera_score = camera_movement_score(filepath)
    print("Camera movement score:", camera_score)

    flash_scor = flash_score(filepath)
    print("Flash score:", flash_scor)

    color_scor = color_score(filepath)
    print("Color score:", color_scor)

    density_scor = density_score(filepath)
    print("Density score:", density_scor)

    final_score = round((scene_score + camera_score + flash_scor + color_scor + density_scor) / 5, 2)

    return jsonify({
        'Scene Change Score': scene_score,
        'Camera Movement Score': camera_score,
        'Flash Score': flash_scor,
        'Color Score': color_scor,
        'Object Density Score': density_scor,
        'Final Score': final_score
    })

if __name__ == '__main__':
    app.run(debug=True)
