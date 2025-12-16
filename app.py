
from flask import Flask, render_template, request, abort, send_file, jsonify
import json
from pathlib import Path
from gtts import gTTS
import os

APP_ROOT = Path(__file__).parent
DATA_PATH = APP_ROOT / "data" / "terms.json"
AUDIO_DIR = APP_ROOT / "static" / "audio"

app = Flask(__name__)

def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_belt(data, belt_id):
    return next((b for b in data["belts"] if b["belt_id"] == belt_id), None)

@app.route("/")
def home():
    data = load_data()
    return render_template("home.html", belts=data["belts"])

@app.route("/belts/<belt_id>")
def belt_terms(belt_id):
    data = load_data()
    belt = get_belt(data, belt_id)
    if not belt:
        abort(404)
    return render_template("terms.html", belt=belt)

@app.route("/audio/<term_id>")
def get_audio(term_id):
    """Generate or serve Korean pronunciation audio"""
    audio_file = AUDIO_DIR / f"{term_id}.mp3"
    
    # If audio doesn't exist, generate it
    if not audio_file.exists():
        data = load_data()
        term = None
        for belt in data["belts"]:
            for t in belt["terms"]:
                if t["id"] == term_id:
                    term = t
                    break
            if term:
                break
        
        if not term:
            abort(404)
        
        # Generate Korean TTS
        try:
            tts = gTTS(text=term["hangul"], lang='ko')
            tts.save(str(audio_file))
        except Exception as e:
            print(f"Error generating audio: {e}")
            abort(500)
    
    return send_file(audio_file, mimetype="audio/mpeg")

if __name__ == "__main__":
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    app.run(debug=True)
