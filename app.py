from flask import Flask, request, jsonify, send_file
import os
import uuid
from spleeter.separator import Separator
import moviepy.editor as mp

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

separator = Separator('spleeter:2stems')

@app.route('/separate', methods=['POST'])
def separate_audio():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file uploaded'}), 400

    video_file = request.files['video']
    filename = str(uuid.uuid4()) + ".mp4"
    video_path = os.path.join(UPLOAD_FOLDER, filename)
    video_file.save(video_path)

    audio_path = os.path.join(OUTPUT_FOLDER, filename.replace('.mp4', '.mp3'))

    video_clip = mp.VideoFileClip(video_path)
    video_clip.audio.write_audiofile(audio_path)

    separator.separate_to_file(audio_path, OUTPUT_FOLDER)

    base_name = filename.replace('.mp4', '')

    return jsonify({
        'voice': f'/outputs/{base_name}/vocals.wav',
        'music': f'/outputs/{base_name}/accompaniment.wav'
    })

@app.route('/outputs/<path:filename>')
def download_file(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
  
