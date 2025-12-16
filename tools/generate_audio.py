
import json
from pathlib import Path
from gtts import gTTS

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "terms.json"
AUDIO_DIR = ROOT / "static" / "audio"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

AUDIO_DIR.mkdir(parents=True, exist_ok=True)

for belt in data["belts"]:
    for term in belt["terms"]:
        out = AUDIO_DIR / f"{term['id']}.mp3"
        if not out.exists():
            tts = gTTS(text=term["hangul"], lang="ko")
            tts.save(out)
            print("Generated:", out.name)
