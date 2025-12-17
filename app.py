
from flask import Flask, render_template, request, abort, send_file, jsonify
import json
from pathlib import Path
from gtts import gTTS
import os
import time
import uuid

import requests


# Centralized belt color mapping (fallback only; primary source is data/terms.json).
BELT_COLORS = {
    "white": "#FFFFFF",
    "yellow": "#FFD700",
    "orange": "#FF8C00",
    "green": "#228B22",
    "blue": "#1E90FF",
    "purple": "#8B008B",
    "brown": "#8B4513",
    "red": "#DC143C",
    "black": "#000000",
}

APP_ROOT = Path(__file__).parent
DATA_PATH = APP_ROOT / "data" / "terms.json"
USER_TERMS_PATH = APP_ROOT / "data" / "user_terms.json"
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


def _get_belt_color(belt: dict) -> str:
    belt_id = (belt.get("belt_id") or "").strip().lower()
    return (belt.get("belt_color") or BELT_COLORS.get(belt_id) or "#FFFFFF").strip()


def _is_dark_hex_color(hex_color: str) -> bool:
    """Return True if hex_color is visually dark.

    Used to decide light/dark text colors on belt-colored headers.
    """
    s = (hex_color or "").strip()
    if not s.startswith("#"):
        return False
    s = s.lstrip("#")
    if len(s) != 6:
        return False
    try:
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
    except ValueError:
        return False

    # Relative luminance (sRGB) approximation.
    # https://www.w3.org/TR/WCAG20/#relativeluminancedef
    def to_lin(v: int) -> float:
        c = v / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    rl = 0.2126 * to_lin(r) + 0.7152 * to_lin(g) + 0.0722 * to_lin(b)
    return rl < 0.45


def _load_user_terms_data() -> dict:
    """Load user-created terms from disk.

    Schema:
      {
        "schema_version": 1,
        "terms": [ {id, english, hangul, romanization?, category?, created_at} ]
      }
    """
    try:
        if not USER_TERMS_PATH.exists():
            return {"schema_version": 1, "terms": []}
        payload = json.loads(USER_TERMS_PATH.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return {"schema_version": 1, "terms": []}
        terms = payload.get("terms")
        if not isinstance(terms, list):
            payload["terms"] = []
        if payload.get("schema_version") != 1:
            # Forward-compatible: treat unknown schema as empty rather than crashing.
            return {"schema_version": 1, "terms": payload.get("terms", []) if isinstance(payload.get("terms"), list) else []}
        return payload
    except Exception:
        return {"schema_version": 1, "terms": []}


def _save_user_terms_data(payload: dict) -> None:
    USER_TERMS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = USER_TERMS_PATH.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(USER_TERMS_PATH)


def _list_user_terms() -> list[dict]:
    return _load_user_terms_data().get("terms", [])


def _find_user_term_by_id(terms: list[dict], term_id: str) -> dict | None:
    for t in terms:
        if t.get("id") == term_id:
            return t
    return None


def _translate_english_to_korean(english_text: str) -> str | None:
    """Best-effort English -> Korean translation.

    Provider is controlled via env var WUTA_TRANSLATION_PROVIDER.
    Supported:
      - none (default if explicitly set)
      - mymemory (no API key; public service, rate-limited)
    """
    provider = (os.environ.get("WUTA_TRANSLATION_PROVIDER") or "mymemory").strip().lower()
    text = (english_text or "").strip()
    if not text:
        return None
    if provider in {"none", "off", "disabled"}:
        return None

    if provider == "mymemory":
        try:
            email = (os.environ.get("WUTA_MYMEMORY_EMAIL") or "").strip()
            params = {
                "q": text,
                "langpair": "en|ko",
            }
            if email:
                params["de"] = email

            resp = requests.get(
                "https://api.mymemory.translated.net/get",
                params=params,
                timeout=8,
                headers={"User-Agent": "WUTA-Taekwondo-Vocabulary-Study-App"},
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            translated = (
                (data or {}).get("responseData", {}) or {}
            ).get("translatedText")
            if not isinstance(translated, str):
                return None

            translated = translated.strip()
            # MyMemory sometimes returns the same string or errors as text.
            if not translated or translated.lower() == text.lower():
                return None
            return translated
        except Exception:
            return None

    # Unknown provider
    return None


def _create_user_term(*, english: str, hangul: str, romanization: str | None = None, category: str | None = None) -> dict:
    now = int(time.time())
    return {
        "id": f"u_{uuid.uuid4().hex}",
        "english": (english or "").strip(),
        "hangul": (hangul or "").strip(),
        "romanization": (romanization or "").strip(),
        "category": (category or "User") .strip() or "User",
        "created_at": now,
        "source": "user",
    }


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

    # Schema v3: bilingual audio includes an English intro phrase and speaks English first.
    if meta and meta.get("schema_version") == 3 and meta.get("mode") == "bilingual":
        return False

    # Legacy cache: without meta, we can't trust what was generated.
    # Regenerate once so we can write the current schema meta and avoid future mismatches.
    if not meta:
        return True

    # Known non-bilingual or unknown schema => try upgrading.
    return True


def _generate_bilingual_mp3(term: dict, out_path: Path):
    """Generate bilingual MP3 (English intro + Korean) to out_path."""
    from pydub import AudioSegment
    import io

    english = (term.get("english") or "").strip()
    hangul = (term.get("hangul") or "").strip()

    # English first: include a short prompt for clarity.
    # Example: "The word is Front Kick."
    english_prompt = f"The word is {english}." if english else ""
    english_tts = gTTS(text=english_prompt or english or hangul, lang="en", slow=False)
    english_audio_bytes = io.BytesIO()
    english_tts.write_to_fp(english_audio_bytes)
    english_audio_bytes.seek(0)

    # Korean stays slow for learning.
    korean_tts = gTTS(text=hangul or english, lang="ko", slow=True)
    korean_audio_bytes = io.BytesIO()
    korean_tts.write_to_fp(korean_audio_bytes)
    korean_audio_bytes.seek(0)

    english_audio = AudioSegment.from_mp3(english_audio_bytes)
    korean_audio = AudioSegment.from_mp3(korean_audio_bytes)
    pause = AudioSegment.silent(duration=650)
    combined = english_audio + pause + korean_audio

    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.export(str(out_path), format="mp3")


def _generate_korean_only_mp3(term: dict, out_path: Path):
    tts = gTTS(text=term["hangul"], lang="ko", slow=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tts.save(str(out_path))


def _generate_english_only_mp3(term: dict, out_path: Path):
    english = (term.get("english") or "").strip()
    hangul = (term.get("hangul") or "").strip()

    # Keep the same learning-friendly prompt as bilingual mode.
    english_prompt = f"The word is {english}." if english else ""
    tts = gTTS(text=english_prompt or english or hangul, lang="en", slow=False)
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
    return render_template("home.html", belts=combined_belts, my_words_count=len(_list_user_terms()))

@app.route("/belts/<belt_id>")
def belt_terms(belt_id):
    data = load_data()
    belt = get_belt(data, belt_id)
    if not belt:
        abort(404)
    belt_color = _get_belt_color(belt)
    # Normalize belt_color so templates/CSS can rely on it.
    try:
        belt["belt_color"] = belt_color
    except Exception:
        pass
    belt_tone = "dark" if _is_dark_hex_color(belt_color) else "light"
    return render_template(
        "terms.html",
        belt=belt,
        total_terms=len(belt.get("terms", [])),
        belt_tone=belt_tone,
    )


@app.route("/my-words")
def my_words():
    terms = sorted(_list_user_terms(), key=lambda t: t.get("created_at", 0), reverse=True)
    return render_template("my_words.html", terms=terms)


@app.route("/my-words/add", methods=["POST"])
def my_words_add():
    english = (request.form.get("english") or "").strip()
    hangul = (request.form.get("hangul") or "").strip()
    romanization = (request.form.get("romanization") or "").strip()
    category = (request.form.get("category") or "User").strip()

    if not english:
        terms = sorted(_list_user_terms(), key=lambda t: t.get("created_at", 0), reverse=True)
        return render_template("my_words.html", terms=terms, error="Please enter an English word or phrase.")

    if not hangul:
        hangul = _translate_english_to_korean(english) or ""

    if not hangul:
        terms = sorted(_list_user_terms(), key=lambda t: t.get("created_at", 0), reverse=True)
        return render_template(
            "my_words.html",
            terms=terms,
            error=(
                "I couldn't auto-translate that right now. Please paste the Korean (Hangul) translation, "
                "or configure WUTA_TRANSLATION_PROVIDER in your environment."
            ),
            pref_english=english,
            pref_category=category,
            pref_romanization=romanization,
        )

    payload = _load_user_terms_data()
    terms_list = payload.get("terms", [])
    if not isinstance(terms_list, list):
        terms_list = []

    new_term = _create_user_term(english=english, hangul=hangul, romanization=romanization, category=category)
    terms_list.append(new_term)
    payload["terms"] = terms_list
    payload["schema_version"] = 1
    _save_user_terms_data(payload)

    terms = sorted(_list_user_terms(), key=lambda t: t.get("created_at", 0), reverse=True)
    return render_template("my_words.html", terms=terms, notice="Added!")


@app.route("/my-words/import", methods=["POST"])
def my_words_import():
    bulk = (request.form.get("bulk_english") or "").strip()
    category = (request.form.get("category") or "User").strip()

    items = []
    for raw in bulk.splitlines():
        s = raw.strip()
        if not s:
            continue
        items.append(s)

    if not items:
        terms = sorted(_list_user_terms(), key=lambda t: t.get("created_at", 0), reverse=True)
        return render_template("my_words.html", terms=terms, error="Paste one English word/phrase per line to import.")

    # Safety limits so we don't hammer translation/audio services.
    if len(items) > 50:
        items = items[:50]

    payload = _load_user_terms_data()
    terms_list = payload.get("terms", [])
    if not isinstance(terms_list, list):
        terms_list = []

    added = 0
    failed = 0
    for english in items:
        hangul = _translate_english_to_korean(english)
        if not hangul:
            failed += 1
            continue
        terms_list.append(_create_user_term(english=english, hangul=hangul, category=category))
        added += 1

    payload["terms"] = terms_list
    payload["schema_version"] = 1
    _save_user_terms_data(payload)

    terms = sorted(_list_user_terms(), key=lambda t: t.get("created_at", 0), reverse=True)
    notice = f"Imported {added} word(s)." + (f" {failed} couldn’t be translated." if failed else "")
    return render_template("my_words.html", terms=terms, notice=notice)


@app.route("/my-words/delete/<term_id>", methods=["POST"])
def my_words_delete(term_id):
    payload = _load_user_terms_data()
    terms_list = payload.get("terms", [])
    if not isinstance(terms_list, list):
        terms_list = []

    terms_list = [t for t in terms_list if t.get("id") != term_id]
    payload["terms"] = terms_list
    payload["schema_version"] = 1
    _save_user_terms_data(payload)

    terms = sorted(_list_user_terms(), key=lambda t: t.get("created_at", 0), reverse=True)
    return render_template("my_words.html", terms=terms, notice="Deleted.")


@app.route("/my-words/train")
def my_words_train():
    terms = _list_user_terms()
    belt = {
        "belt_id": "my_words",
        "belt_name": "My Words",
        "belt_color": "#ff9f1a",
        "terms": terms,
    }
    belt_color = _get_belt_color(belt)
    belt_tone = "dark" if _is_dark_hex_color(belt_color) else "light"
    return render_template("terms.html", belt=belt, total_terms=len(terms), belt_tone=belt_tone)

@app.route("/audio/<term_id>")
def get_audio(term_id):
    """Generate or serve Korean pronunciation audio"""
    # Ensure directory exists even under gunicorn (where __main__ doesn't run).
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    mode = (request.args.get("mode") or "bilingual").strip().lower()
    want_korean_only = mode in {"korean", "ko", "korean_only"}
    want_english_only = mode in {"english", "en", "english_only"}

    # Keep separate cache files per mode so toggling doesn't overwrite tracks.
    audio_suffix = ".ko" if want_korean_only else (".en" if want_english_only else "")
    audio_file = AUDIO_DIR / f"{term_id}{audio_suffix}.mp3"
    audio_meta = AUDIO_DIR / f"{term_id}{audio_suffix}.meta.json"

    data = load_data()
    term = _find_term_by_id(data, term_id)
    if not term:
        user_terms = _list_user_terms()
        term = _find_user_term_by_id(user_terms, term_id)
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

    # English-only mode: generate once and keep it.
    if want_english_only:
        if not audio_file.exists():
            tmp_file = AUDIO_DIR / f"{term_id}{audio_suffix}.tmp.mp3"
            try:
                _generate_english_only_mp3(term, tmp_file)
                tmp_file.replace(audio_file)
                _write_audio_meta(
                    audio_meta,
                    {
                        "schema_version": 3,
                        "mode": "english_only",
                        "term_id": term_id,
                        "generated_at": int(time.time()),
                        "prefix": "the word is",
                    },
                )
            except Exception as e:
                try:
                    if tmp_file.exists():
                        tmp_file.unlink()
                except Exception:
                    pass
                print(f"Error generating English-only audio for {term_id}: {e}")
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
                    "schema_version": 3,
                    "mode": "bilingual",
                    "term_id": term_id,
                    "generated_at": int(time.time()),
                    "voice_order": "en_then_ko",
                    "prefix": "the word is",
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
