from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile

# Assume these functions are already defined and imported
from scenechange import analyze_scene_change
from saturation_brightness import analyze_saturation_brightness
from camera_movement import analyze_camera_movement
from flashing_effects import analyze_flashing_effects
from object_density import analyze_object_density

app = Flask(__name__)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    if 'video' not in request.files:
        return jsonify({'error': 'No video uploaded'}), 400

    video = request.files['video']
    filename = secure_filename(video.filename)

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, filename)
        video.save(filepath)

        scores = {
            'Scene Change Frequency': analyze_scene_change(filepath),
            'Color Saturation & Brightness': analyze_saturation_brightness(filepath),
            'Camera Movement': analyze_camera_movement(filepath),
            'Flashing Effects': analyze_flashing_effects(filepath),
            'Object Density': analyze_object_density(filepath)
        }

        final_score = sum(scores.values()) / len(scores)

        return jsonify({
            'scores': scores,
            'final_score': final_score
        })

if __name__ == '__main__':
    app.run(debug=True)
