from flask import Flask, request, jsonify
import os
import tempfile

from scene_change_analysis import scene_change_score
from color_score_analysis import color_score
from camera_movement_analysis import camera_movement_score
from flash_score_analysis import flash_score
from density_score_analysis import density_score

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video = request.files['video']

    if video.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            video.save(tmp.name)
            video_path = tmp.name

        # Run analysis
        scene_score = scene_change_score(video_path)
        color = color_score(video_path)
        camera = camera_movement_score(video_path)
        flash = flash_score(video_path)
        density = density_score(video_path)

        scores = {
            'scene_change_score': round(scene_score, 2),
            'color_score': round(color, 2),
            'camera_movement_score': round(camera, 2),
            'flash_score': round(flash, 2),
            'density_score': round(density, 2)
        }

        # Final weighted score (simple average for now)
        final_score = round(sum(scores.values()) / len(scores), 2)
        scores['final_score'] = final_score

        os.remove(video_path)

        return jsonify(scores)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT env var if set
    app.run(host='0.0.0.0', port=port, debug=True)
