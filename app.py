
from flask import Flask, render_template, request, abort
import json
from pathlib import Path

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

if __name__ == "__main__":
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    app.run(debug=True)
