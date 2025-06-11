from flask import Flask, request, jsonify
import os
import uuid

# Import your analysis functions
from scenechange import analyze_scene_changes
from saturation_brightness import analyze_color_score
from camera_movement import analyze_camera_movement
from flashing_effects import analyze_flashing_effects
from object_density import analyze_object_density

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/analyze", methods=["POST"])
def analyze_video():
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files["video"]
    filename = f"{uuid.uuid4()}.mp4"
    video_path = os.path.join(UPLOAD_FOLDER, filename)
    video_file.save(video_path)

    try:
        scene_score = analyze_scene_changes(video_path)
        color_score = analyze_color_score(video_path)
        motion_score = analyze_camera_movement(video_path)
        flash_score = analyze_flashing_effects(video_path)
        density_score = analyze_object_density(video_path)

        # Weighted final score (can be customized)
        final_score = round((scene_score + color_score + motion_score + flash_score + density_score) / 5, 2)

        return jsonify({
            "scene_change_score": scene_score,
            "color_score": color_score,
            "camera_movement_score": motion_score,
            "flashing_effects_score": flash_score,
            "object_density_score": density_score,
            "final_score": final_score
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
