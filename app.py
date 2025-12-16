
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

def combine_belts_with_tips(belts):
    """Combine main belt colors with their tips into single entries"""
    combined = []
    main_colors = ['white', 'yellow', 'orange', 'green', 'blue', 'purple', 'brown', 'red', 'black']
    
    for color in main_colors:
        # Find main belt
        main_belt = next((b for b in belts if b["belt_id"] == color), None)
        if not main_belt:
            continue
            
        # Find tip belt
        tip_belt = next((b for b in belts if b["belt_id"] == f"{color}_tip"), None)
        
        # Combine terms
        combined_terms = main_belt["terms"].copy()
        if tip_belt:
            combined_terms.extend(tip_belt["terms"])
        
        # Create combined belt entry
        combined_belt = {
            "belt_id": color,
            "belt_name": main_belt["belt_name"],
            "belt_color": main_belt["belt_color"],
            "terms": combined_terms
        }
        if "tip_color" in main_belt:
            combined_belt["tip_color"] = main_belt["tip_color"]
            
        combined.append(combined_belt)
    
    return combined

@app.route("/")
def home():
    data = load_data()
    combined_belts = combine_belts_with_tips(data["belts"])
    return render_template("home.html", belts=combined_belts)

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
        
        # Generate bilingual TTS: Korean first, then English translation
        try:
            from pydub import AudioSegment
            import io
            
            # Create Korean audio (slow)
            korean_tts = gTTS(text=term["hangul"], lang='ko', slow=True)
            korean_audio_bytes = io.BytesIO()
            korean_tts.write_to_fp(korean_audio_bytes)
            korean_audio_bytes.seek(0)
            
            # Create English audio (slow)
            english_tts = gTTS(text=term["english"], lang='en', slow=True)
            english_audio_bytes = io.BytesIO()
            english_tts.write_to_fp(english_audio_bytes)
            english_audio_bytes.seek(0)
            
            # Combine: Korean + pause + English
            korean_audio = AudioSegment.from_mp3(korean_audio_bytes)
            english_audio = AudioSegment.from_mp3(english_audio_bytes)
            pause = AudioSegment.silent(duration=500)  # 500ms pause
            
            combined = korean_audio + pause + english_audio
            combined.export(str(audio_file), format="mp3")
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            # Fallback to Korean only if pydub not available
            try:
                tts = gTTS(text=term["hangul"], lang='ko', slow=True)
                tts.save(str(audio_file))
            except:
                abort(500)
    
    return send_file(audio_file, mimetype="audio/mpeg")

if __name__ == "__main__":
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    # Get port from environment variable (for production) or default to 5000
    port = int(os.environ.get("PORT", 5000))
    # Disable debug in production
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)
