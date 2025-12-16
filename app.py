
from flask import Flask, render_template, request, abort, send_file, jsonify
import json
from pathlib import Path
from gtts import gTTS
import os
import time

APP_ROOT = Path(__file__).parent
DATA_PATH = APP_ROOT / "data" / "terms.json"
AUDIO_DIR = APP_ROOT / "static" / "audio"

app = Flask(__name__)


def _find_term_by_id(data, term_id):
    for belt in data.get("belts", []):
        for term in belt.get("terms", []):
            if term.get("id") == term_id:
                return term
            # Backward compatibility: allow requesting audio using a previous id.
            if term.get("legacy_id") == term_id:
                return term
    return None


def _load_audio_meta(meta_path: Path):
    try:
        if not meta_path.exists():
            return None
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_audio_meta(meta_path: Path, payload: dict):
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _should_upgrade_audio(audio_path: Path, meta: dict | None):
    """Return True if we should attempt to regenerate bilingual audio.

    We use a sidecar meta file to avoid repeatedly regenerating.
    For legacy files without meta, we use a conservative size heuristic.
    """
    if not audio_path.exists():
        return True

    if meta and meta.get("schema_version") == 2 and meta.get("mode") == "bilingual":
        return False

    # Legacy cache: if we don't know, only upgrade obviously-small files.
    if not meta:
        try:
            # Korean-only files were typically a few KB. Bilingual is usually much larger.
            # Heuristic: upgrade if < 7KB.
            return audio_path.stat().st_size < 7000
        except Exception:
            return False

    # Known non-bilingual or unknown schema => try upgrading.
    return True


def _generate_bilingual_mp3(term: dict, out_path: Path):
    """Generate Korean + pause + English MP3 to out_path."""
    from pydub import AudioSegment
    import io

    korean_tts = gTTS(text=term["hangul"], lang="ko", slow=True)
    korean_audio_bytes = io.BytesIO()
    korean_tts.write_to_fp(korean_audio_bytes)
    korean_audio_bytes.seek(0)

    # English translation at a normal pace (Korean stays slow for learning).
    english_tts = gTTS(text=term["english"], lang="en", slow=False)
    english_audio_bytes = io.BytesIO()
    english_tts.write_to_fp(english_audio_bytes)
    english_audio_bytes.seek(0)

    korean_audio = AudioSegment.from_mp3(korean_audio_bytes)
    english_audio = AudioSegment.from_mp3(english_audio_bytes)
    pause = AudioSegment.silent(duration=650)
    combined = korean_audio + pause + english_audio

    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.export(str(out_path), format="mp3")


def _generate_korean_only_mp3(term: dict, out_path: Path):
    tts = gTTS(text=term["hangul"], lang="ko", slow=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tts.save(str(out_path))

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
    # Ensure directory exists even under gunicorn (where __main__ doesn't run).
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    mode = (request.args.get("mode") or "bilingual").strip().lower()
    want_korean_only = mode in {"korean", "ko", "korean_only"}

    # Keep separate cache files per mode so toggling doesn't overwrite the bilingual track.
    audio_suffix = ".ko" if want_korean_only else ""
    audio_file = AUDIO_DIR / f"{term_id}{audio_suffix}.mp3"
    audio_meta = AUDIO_DIR / f"{term_id}{audio_suffix}.meta.json"

    data = load_data()
    term = _find_term_by_id(data, term_id)
    if not term:
        abort(404)

    meta = _load_audio_meta(audio_meta)

    # Korean-only mode: generate once and keep it.
    if want_korean_only:
        if not audio_file.exists():
            tmp_file = AUDIO_DIR / f"{term_id}{audio_suffix}.tmp.mp3"
            try:
                _generate_korean_only_mp3(term, tmp_file)
                tmp_file.replace(audio_file)
                _write_audio_meta(
                    audio_meta,
                    {
                        "schema_version": 2,
                        "mode": "korean_only",
                        "term_id": term_id,
                        "generated_at": int(time.time()),
                    },
                )
            except Exception as e:
                try:
                    if tmp_file.exists():
                        tmp_file.unlink()
                except Exception:
                    pass
                print(f"Error generating Korean-only audio for {term_id}: {e}")
                abort(500)

        return send_file(audio_file, mimetype="audio/mpeg")

    needs_upgrade = _should_upgrade_audio(audio_file, meta)

    if needs_upgrade:
        tmp_file = AUDIO_DIR / f"{term_id}.tmp.mp3"
        try:
            _generate_bilingual_mp3(term, tmp_file)

            # Atomic-ish replace: write temp then replace.
            tmp_file.replace(audio_file)
            _write_audio_meta(
                audio_meta,
                {
                    "schema_version": 2,
                    "mode": "bilingual",
                    "term_id": term_id,
                    "generated_at": int(time.time()),
                },
            )
        except Exception as e:
            # Don't clobber an existing file if bilingual generation fails mid-session.
            try:
                if tmp_file.exists():
                    tmp_file.unlink()
            except Exception:
                pass

            print(f"Error generating bilingual audio for {term_id}: {e}")

            # If we have no audio at all yet, fall back to Korean-only so the app still works.
            if not audio_file.exists():
                try:
                    _generate_korean_only_mp3(term, audio_file)
                    _write_audio_meta(
                        audio_meta,
                        {
                            "schema_version": 2,
                            "mode": "korean_only",
                            "term_id": term_id,
                            "generated_at": int(time.time()),
                            "error": str(e),
                        },
                    )
                except Exception:
                    abort(500)
            else:
                # Keep existing audio, but record that we couldn't upgrade right now.
                try:
                    _write_audio_meta(
                        audio_meta,
                        {
                            "schema_version": 2,
                            "mode": meta.get("mode") if meta else "unknown",
                            "term_id": term_id,
                            "generated_at": int(time.time()),
                            "upgrade_failed": True,
                            "error": str(e),
                        },
                    )
                except Exception:
                    pass
    
    return send_file(audio_file, mimetype="audio/mpeg")

if __name__ == "__main__":
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    # Get port from environment variable (for production) or default to 5000
    port = int(os.environ.get("PORT", 5000))
    # Disable debug in production
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)
