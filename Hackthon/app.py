from flask import Flask, render_template, request, jsonify
from utils import transcribe_audio, analyze_transcript
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['audio']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    transcript = transcribe_audio(filepath)
    analysis = analyze_transcript(transcript)

    return jsonify({
        "transcript": transcript,
        "summary": analysis['summary'],
        "action_items": analysis['actions'],
        "email": analysis['email']
    })

if __name__ == '__main__':
    app.run(debug=True)
