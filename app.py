
from flask import Flask, render_template, request, abort, send_file, jsonify, session, redirect, url_for
import json
from pathlib import Path
from gtts import gTTS
import os
import time
import uuid
import re
import functools
import csv
import io

from werkzeug.security import check_password_hash, generate_password_hash

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
CUSTOM_DICT_PATH = APP_ROOT / "data" / "custom_dictionary.json"
USERS_PATH = APP_ROOT / "data" / "users.json"
AUDIO_DIR = APP_ROOT / "static" / "audio"

app = Flask(__name__)

# Session security: set FLASK_SECRET_KEY in your environment for production.
# We still provide a dev fallback so the app boots for local usage.
app.secret_key = (
    (os.environ.get("FLASK_SECRET_KEY") or "").strip()
    or (os.environ.get("SECRET_KEY") or "").strip()
    or "dev-only-change-me"
)


def _load_users_data() -> dict:
    """Load registered users from disk.

    Schema:
      {
        "schema_version": 1,
        "users": [
          {"id": str, "username": str, "email": str, "password_hash": str, "created_at": int}
        ]
      }
    """
    try:
        if not USERS_PATH.exists():
            return {"schema_version": 1, "users": []}
        payload = json.loads(USERS_PATH.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return {"schema_version": 1, "users": []}
        if payload.get("schema_version") != 1:
            # Forward-compatible: keep data but ensure required keys exist.
            users = payload.get("users", [])
            return {"schema_version": 1, "users": users if isinstance(users, list) else []}
        users = payload.get("users")
        if not isinstance(users, list):
            payload["users"] = []
        return payload
    except Exception:
        return {"schema_version": 1, "users": []}


def _save_users_data(payload: dict) -> None:
    USERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = USERS_PATH.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(USERS_PATH)


def _normalize_username(username: str) -> str:
    s = (username or "").strip()
    # Keep it kid-friendly/simple: letters, numbers, underscore, dash.
    s = re.sub(r"[^a-zA-Z0-9_-]", "", s)
    return s


def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def _find_user_by_id(user_id: str) -> dict | None:
    if not user_id:
        return None
    payload = _load_users_data()
    for u in payload.get("users", []) or []:
        if isinstance(u, dict) and u.get("id") == user_id:
            return u
    return None


def _find_user_by_username(username: str) -> dict | None:
    uname = _normalize_username(username)
    if not uname:
        return None
    payload = _load_users_data()
    for u in payload.get("users", []) or []:
        if not isinstance(u, dict):
            continue
        if (u.get("username") or "").lower() == uname.lower():
            return u
    return None


def _find_user_by_email(email: str) -> dict | None:
    em = _normalize_email(email)
    if not em:
        return None
    payload = _load_users_data()
    for u in payload.get("users", []) or []:
        if not isinstance(u, dict):
            continue
        if _normalize_email(u.get("email") or "") == em:
            return u
    return None


def _create_user(*, username: str, email: str, password: str) -> dict:
    now = int(time.time())
    return {
        "id": f"usr_{uuid.uuid4().hex}",
        "username": _normalize_username(username),
        "email": _normalize_email(email),
        "password_hash": generate_password_hash(password),
        "created_at": now,
    }


def _get_current_user() -> dict | None:
    user_id = session.get("user_id")
    if not isinstance(user_id, str) or not user_id:
        return None
    u = _find_user_by_id(user_id)
    if not u:
        # Stale session.
        try:
            session.pop("user_id", None)
        except Exception:
            pass
        return None
    return u


def login_required(view_func):
    """Decorator to require a logged-in user.

    Redirects to /login?next=... if not authenticated.
    """
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        if not _get_current_user():
            next_url = _safe_next_url(request.path)
            return redirect(url_for("login", next=next_url))
        return view_func(*args, **kwargs)
    return wrapper


@app.context_processor
def _inject_current_user():
    return {"current_user": _get_current_user()}


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


def _load_custom_dictionary() -> dict:
    """Load admin-managed custom dictionary entries.

    Schema:
      {
        "schema_version": 1,
        "entries": [ {"english": str, "hangul": str, "romanization"?: str, "category"?: str, "created_at": int, "updated_at": int} ]
      }
    """
    try:
        if not CUSTOM_DICT_PATH.exists():
            return {"schema_version": 1, "entries": []}
        payload = json.loads(CUSTOM_DICT_PATH.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return {"schema_version": 1, "entries": []}
        if payload.get("schema_version") != 1:
            return {"schema_version": 1, "entries": payload.get("entries", []) if isinstance(payload.get("entries"), list) else []}
        entries = payload.get("entries")
        if not isinstance(entries, list):
            payload["entries"] = []
        return payload
    except Exception:
        return {"schema_version": 1, "entries": []}


def _save_custom_dictionary(payload: dict) -> None:
    CUSTOM_DICT_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = CUSTOM_DICT_PATH.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(CUSTOM_DICT_PATH)


def _list_custom_dictionary_entries() -> list[dict]:
    return _load_custom_dictionary().get("entries", [])


def _admin_token_required() -> str:
    return (os.environ.get("WUTA_ADMIN_TOKEN") or "").strip()


def _check_admin_token() -> bool:
    required = _admin_token_required()
    if not required:
        return False
    supplied = (request.args.get("token") or request.form.get("token") or "").strip()
    return supplied == required


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
      - dictionary (offline; uses built-in WUTA vocab only)
      - none (disable; require manual Hangul entry)
      - mymemory (online; no API key; public service, rate-limited)
    """
    provider = (os.environ.get("WUTA_TRANSLATION_PROVIDER") or "dictionary").strip().lower()
    text = (english_text or "").strip()
    if not text:
        return None
    if provider in {"none", "off", "disabled"}:
        return None

    if provider in {"dictionary", "dict", "local", "offline"}:
        hit = _lookup_hangul_from_vocab(text)
        return hit or None

    if provider == "mymemory":
        return _translate_via_mymemory(text)

    # Unknown provider
    return None


def _translate_via_mymemory(text: str) -> str | None:
    """Online English->Korean translation via MyMemory (best-effort)."""
    try:
        src = (text or "").strip()
        if not src:
            return None

        email = (os.environ.get("WUTA_MYMEMORY_EMAIL") or "").strip()
        params = {
            "q": src,
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
        translated = (((data or {}).get("responseData", {}) or {})).get("translatedText")
        if not isinstance(translated, str):
            return None

        translated = translated.strip()
        # MyMemory sometimes returns the same string or errors as text.
        if not translated or translated.lower() == src.lower():
            return None
        return translated
    except Exception:
        return None


_HANGUL_RE = re.compile(r"[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7A3]")


def _has_hangul(text: str) -> bool:
    """Return True if text contains any Hangul characters."""
    if not isinstance(text, str):
        return False
    return bool(_HANGUL_RE.search(text))


def _clean_korean_candidate(text: str) -> str:
    """Light normalization for Korean strings coming from user input or translation services."""
    if not isinstance(text, str):
        return ""
    return " ".join(text.strip().split())


def _normalize_english_key(text: str) -> str:
    """Normalize an English phrase for stable matching (case/whitespace/punctuation-insensitive)."""
    if not isinstance(text, str):
        return ""
    s = text.strip().lower()
    # Replace any non-alphanumeric with spaces, collapse whitespace.
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = " ".join(s.split())
    return s


@functools.lru_cache(maxsize=4)
def _english_to_hangul_index(data_mtime: float) -> dict[str, str]:
    """Build a lookup of normalized English -> Hangul using the canonical vocab dataset."""
    try:
        data = load_data()
    except Exception:
        return {}

    idx: dict[str, str] = {}
    for belt in (data or {}).get("belts", []) or []:
        for term in (belt or {}).get("terms", []) or []:
            if not isinstance(term, dict):
                continue
            eng = (term.get("english") or "").strip()
            hangul = _clean_korean_candidate(term.get("hangul") or "")
            if not eng or not _has_hangul(hangul):
                continue
            key = _normalize_english_key(eng)
            if not key:
                continue
            # First write wins so we keep the earliest canonical mapping.
            idx.setdefault(key, hangul)

    # Layer in admin-managed custom dictionary entries (override canonical if needed).
    try:
        custom_payload = _load_custom_dictionary()
        custom_entries = custom_payload.get("entries", []) if isinstance(custom_payload, dict) else []
    except Exception:
        custom_entries = []

    for e in custom_entries or []:
        if not isinstance(e, dict):
            continue
        eng = (e.get("english") or "").strip()
        hangul = _clean_korean_candidate(e.get("hangul") or "")
        if not eng or not _has_hangul(hangul):
            continue
        key = _normalize_english_key(eng)
        if not key:
            continue
        # Custom entries override canonical.
        idx[key] = hangul
    return idx


def _lookup_hangul_from_vocab(english: str) -> str:
    """Return Hangul from built-in vocab for an English phrase, else empty string."""
    key = _normalize_english_key(english)
    if not key:
        return ""
    try:
        mtime = DATA_PATH.stat().st_mtime
    except Exception:
        mtime = 0.0
    idx = _english_to_hangul_index(mtime)
    return idx.get(key, "")


def _best_effort_hangul_for_english(english: str) -> str:
    """Translate English to Hangul if possible; otherwise return empty string."""
    # 1) Deterministic lookup from our curated dataset.
    vocab_hit = _lookup_hangul_from_vocab(english)
    if vocab_hit:
        return vocab_hit

    # 2) Online translation (optional) for unknown phrases only.
    # If WUTA_TRANSLATION_PROVIDER is 'dictionary', this is disabled unless WUTA_TRANSLATION_FALLBACK is set.
    provider = (os.environ.get("WUTA_TRANSLATION_PROVIDER") or "dictionary").strip().lower()
    fallback = (os.environ.get("WUTA_TRANSLATION_FALLBACK") or "").strip().lower()

    translated = ""
    if provider == "mymemory":
        translated = _translate_via_mymemory(english) or ""
    elif provider in {"dictionary", "dict", "local", "offline"} and fallback in {"mymemory"}:
        translated = _translate_via_mymemory(english) or ""
    else:
        # Any other provider types: keep legacy behavior (if configured).
        translated = _translate_english_to_korean(english) or ""

    translated = _clean_korean_candidate(translated)
    return translated if _has_hangul(translated) else ""


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
    hangul = _clean_korean_candidate(term.get("hangul") or "")
    romanization = (term.get("romanization") or "").strip()

    # English first: include a short prompt for clarity.
    # Example: "The word is Front Kick."
    english_prompt = f"The word is {english}." if english else ""
    english_tts = gTTS(text=english_prompt or english or hangul, lang="en", slow=False)
    english_audio_bytes = io.BytesIO()
    english_tts.write_to_fp(english_audio_bytes)
    english_audio_bytes.seek(0)

    # Korean stays slow for learning.
    # IMPORTANT: never feed English into a Korean voice (sounds like a "Korean accent").
    korean_text = hangul if _has_hangul(hangul) else ""
    if not korean_text and english:
        korean_text = _best_effort_hangul_for_english(english)

    korean_audio = None
    if korean_text:
        korean_tts = gTTS(text=korean_text, lang="ko", slow=True)
        korean_audio_bytes = io.BytesIO()
        korean_tts.write_to_fp(korean_audio_bytes)
        korean_audio_bytes.seek(0)
        korean_audio = AudioSegment.from_mp3(korean_audio_bytes)
    elif romanization:
        # Last-resort fallback: speak romanization with an English voice so it doesn't sound like a bad "translation".
        rom_tts = gTTS(text=romanization, lang="en", slow=False)
        rom_audio_bytes = io.BytesIO()
        rom_tts.write_to_fp(rom_audio_bytes)
        rom_audio_bytes.seek(0)
        korean_audio = AudioSegment.from_mp3(rom_audio_bytes)

    english_audio = AudioSegment.from_mp3(english_audio_bytes)
    if korean_audio is not None:
        pause = AudioSegment.silent(duration=650)
        combined = english_audio + pause + korean_audio
    else:
        combined = english_audio

    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.export(str(out_path), format="mp3")


def _generate_korean_only_mp3(term: dict, out_path: Path):
    hangul = _clean_korean_candidate(term.get("hangul") or "")
    if not _has_hangul(hangul):
        # Try translating from English before giving up.
        hangul = _best_effort_hangul_for_english((term.get("english") or "").strip())
    if not _has_hangul(hangul):
        raise ValueError("No valid Hangul available for Korean-only audio")

    tts = gTTS(text=hangul, lang="ko", slow=True)
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


def _safe_next_url(next_url: str) -> str:
    """Very small open-redirect guard.

    Only allow relative paths like '/my-words'.
    """
    s = (next_url or "").strip()
    if not s:
        return ""
    if s.startswith("/") and not s.startswith("//") and "\n" not in s and "\r" not in s:
        return s
    return ""


@app.route("/register", methods=["GET", "POST"])
def register():
    if _get_current_user():
        return redirect(url_for("home"))

    if request.method == "GET":
        return render_template("register.html")

    username_raw = (request.form.get("username") or "").strip()
    email_raw = (request.form.get("email") or "").strip()
    password = (request.form.get("password") or "")
    password2 = (request.form.get("password2") or "")

    username = _normalize_username(username_raw)
    email = _normalize_email(email_raw)
    next_url = _safe_next_url(request.args.get("next") or request.form.get("next") or "")

    if len(username) < 3:
        return render_template(
            "register.html",
            error="Username must be at least 3 characters (letters/numbers/_/-).",
            pref_username=username_raw,
            pref_email=email_raw,
            next=next_url,
        )
    if "@" not in email or "." not in email:
        return render_template(
            "register.html",
            error="Please enter a valid email address.",
            pref_username=username_raw,
            pref_email=email_raw,
            next=next_url,
        )
    if len(password) < 6:
        return render_template(
            "register.html",
            error="Password must be at least 6 characters.",
            pref_username=username_raw,
            pref_email=email_raw,
            next=next_url,
        )
    if password != password2:
        return render_template(
            "register.html",
            error="Passwords do not match.",
            pref_username=username_raw,
            pref_email=email_raw,
            next=next_url,
        )

    if _find_user_by_username(username):
        return render_template(
            "register.html",
            error="That username is already taken.",
            pref_username=username_raw,
            pref_email=email_raw,
            next=next_url,
        )
    if _find_user_by_email(email):
        return render_template(
            "register.html",
            error="An account with that email already exists.",
            pref_username=username_raw,
            pref_email=email_raw,
            next=next_url,
        )

    payload = _load_users_data()
    users = payload.get("users", [])
    if not isinstance(users, list):
        users = []

    new_user = _create_user(username=username, email=email, password=password)
    users.append(new_user)
    payload["schema_version"] = 1
    payload["users"] = users
    _save_users_data(payload)

    session["user_id"] = new_user["id"]
    return redirect(next_url or url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if _get_current_user():
        return redirect(url_for("home"))

    next_url = _safe_next_url(request.args.get("next") or request.form.get("next") or "")

    if request.method == "GET":
        return render_template("login.html", next=next_url)

    identifier = (request.form.get("identifier") or "").strip()
    password = (request.form.get("password") or "")

    user = None
    if "@" in identifier:
        user = _find_user_by_email(identifier)
    if not user:
        user = _find_user_by_username(identifier)

    if not user:
        return render_template(
            "login.html",
            error="No account found for that username/email.",
            pref_identifier=identifier,
            next=next_url,
        )

    if not check_password_hash((user.get("password_hash") or ""), password):
        return render_template(
            "login.html",
            error="Incorrect password.",
            pref_identifier=identifier,
            next=next_url,
        )

    session["user_id"] = user.get("id")
    return redirect(next_url or url_for("home"))


@app.route("/logout")
def logout():
    try:
        session.pop("user_id", None)
    except Exception:
        pass
    return redirect(url_for("home"))


@app.route("/account")
@login_required
def account():
    # current_user is injected via context processor, but we also fetch it here for safety.
    user = _get_current_user()
    return render_template("account.html", user=user)


@app.route("/account/delete", methods=["POST"])
@login_required
def account_delete():
    user = _get_current_user()
    if not user:
        return redirect(url_for("home"))

    password = (request.form.get("password") or "")
    confirm = (request.form.get("confirm") or "").strip().lower()

    if confirm not in {"yes", "on", "true", "1"}:
        return render_template("account.html", user=user, error="Please confirm account deletion.")

    if not check_password_hash((user.get("password_hash") or ""), password):
        return render_template("account.html", user=user, error="Incorrect password.")

    payload = _load_users_data()
    users = payload.get("users", [])
    if not isinstance(users, list):
        users = []

    uid = user.get("id")
    users = [u for u in users if not (isinstance(u, dict) and u.get("id") == uid)]
    payload["schema_version"] = 1
    payload["users"] = users
    _save_users_data(payload)

    try:
        session.pop("user_id", None)
    except Exception:
        pass

    # Redirect home; the account is now removed.
    return redirect(url_for("home"))

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

    hangul = _clean_korean_candidate(hangul)
    if not hangul:
        hangul = _best_effort_hangul_for_english(english)

    # Tighten: don't accept English pasted into the Hangul field.
    if hangul and not _has_hangul(hangul):
        hangul = ""

    if not hangul:
        terms = sorted(_list_user_terms(), key=lambda t: t.get("created_at", 0), reverse=True)
        return render_template(
            "my_words.html",
            terms=terms,
            error=(
                "I couldn't auto-translate that right now (or the Hangul field didn’t look like Korean). "
                "Please paste the Korean (Hangul) translation (e.g., '앞차기'), "
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
        hangul = _best_effort_hangul_for_english(english)
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


@app.route("/my-words/repair", methods=["POST"])
def my_words_repair():
    """Repair saved user terms whose Hangul is missing/invalid by attempting auto-translation."""
    payload = _load_user_terms_data()
    terms_list = payload.get("terms", [])
    if not isinstance(terms_list, list):
        terms_list = []

    fixed = 0
    failed = 0
    for t in terms_list:
        if not isinstance(t, dict):
            continue
        english = (t.get("english") or "").strip()
        hangul = _clean_korean_candidate(t.get("hangul") or "")

        # Only repair if Hangul is missing or doesn't actually contain Hangul.
        if _has_hangul(hangul):
            continue
        if not english:
            failed += 1
            continue

        new_hangul = _best_effort_hangul_for_english(english)
        if not new_hangul:
            failed += 1
            continue

        t["hangul"] = new_hangul
        fixed += 1

    payload["terms"] = terms_list
    payload["schema_version"] = 1
    _save_user_terms_data(payload)

    terms = sorted(_list_user_terms(), key=lambda t: t.get("created_at", 0), reverse=True)
    notice = f"Repaired {fixed} word(s)." + (f" {failed} could not be translated." if failed else "")
    return render_template("my_words.html", terms=terms, notice=notice)


@app.route("/admin/dictionary")
def admin_dictionary():
    token_required = _admin_token_required()
    if not token_required:
        return render_template(
            "admin_dictionary.html",
            entries=[],
            token="",
            error="Admin dictionary is disabled. Set WUTA_ADMIN_TOKEN in your environment to enable it.",
        )
    if not _check_admin_token():
        return render_template(
            "admin_dictionary.html",
            entries=[],
            token="",
            error="Unauthorized. Provide ?token=...",
        )

    token = (request.args.get("token") or "").strip()
    entries = sorted(_list_custom_dictionary_entries(), key=lambda e: (e.get("english") or "").lower())
    return render_template("admin_dictionary.html", entries=entries, token=token)


@app.route("/admin/dictionary/save", methods=["POST"])
def admin_dictionary_save():
    if not _check_admin_token():
        abort(403)

    english = (request.form.get("english") or "").strip()
    hangul = _clean_korean_candidate(request.form.get("hangul") or "")
    romanization = (request.form.get("romanization") or "").strip()
    category = (request.form.get("category") or "").strip()
    token = (request.form.get("token") or "").strip()

    if not english:
        entries = sorted(_list_custom_dictionary_entries(), key=lambda e: (e.get("english") or "").lower())
        return render_template("admin_dictionary.html", entries=entries, token=token, error="English is required.")

    if not _has_hangul(hangul):
        entries = sorted(_list_custom_dictionary_entries(), key=lambda e: (e.get("english") or "").lower())
        return render_template("admin_dictionary.html", entries=entries, token=token, error="Hangul is required (must contain Korean characters).")

    payload = _load_custom_dictionary()
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        entries = []

    now = int(time.time())
    updated = False
    for e in entries:
        if not isinstance(e, dict):
            continue
        if _normalize_english_key(e.get("english") or "") == _normalize_english_key(english):
            e["english"] = english
            e["hangul"] = hangul
            if romanization:
                e["romanization"] = romanization
            else:
                e.pop("romanization", None)
            if category:
                e["category"] = category
            else:
                e.pop("category", None)
            e["updated_at"] = now
            updated = True
            break

    if not updated:
        entries.append(
            {
                "english": english,
                "hangul": hangul,
                "romanization": romanization,
                "category": category,
                "created_at": now,
                "updated_at": now,
            }
        )

    payload["schema_version"] = 1
    payload["entries"] = entries
    _save_custom_dictionary(payload)
    # Bust the cached index so new entries are immediately used.
    try:
        _english_to_hangul_index.cache_clear()
    except Exception:
        pass

    entries_sorted = sorted(_list_custom_dictionary_entries(), key=lambda e: (e.get("english") or "").lower())
    notice = "Updated." if updated else "Added."
    return render_template("admin_dictionary.html", entries=entries_sorted, token=token, notice=notice)


@app.route("/admin/dictionary/delete", methods=["POST"])
def admin_dictionary_delete():
    if not _check_admin_token():
        abort(403)
    token = (request.form.get("token") or "").strip()
    english = (request.form.get("english") or "").strip()
    if not english:
        abort(400)

    payload = _load_custom_dictionary()
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        entries = []

    key = _normalize_english_key(english)
    entries = [e for e in entries if _normalize_english_key((e or {}).get("english") or "") != key]
    payload["entries"] = entries
    payload["schema_version"] = 1
    _save_custom_dictionary(payload)
    try:
        _english_to_hangul_index.cache_clear()
    except Exception:
        pass

    entries_sorted = sorted(_list_custom_dictionary_entries(), key=lambda e: (e.get("english") or "").lower())
    return render_template("admin_dictionary.html", entries=entries_sorted, token=token, notice="Deleted.")


@app.route("/admin/dictionary/import", methods=["POST"])
def admin_dictionary_import():
    if not _check_admin_token():
        abort(403)
    token = (request.form.get("token") or "").strip()

    f = request.files.get("csvfile")
    if not f:
        entries_sorted = sorted(_list_custom_dictionary_entries(), key=lambda e: (e.get("english") or "").lower())
        return render_template("admin_dictionary.html", entries=entries_sorted, token=token, error="Please choose a CSV file.")

    try:
        raw = f.read()
        # UTF-8 with BOM supported.
        text = raw.decode("utf-8-sig", errors="replace")
    except Exception:
        entries_sorted = sorted(_list_custom_dictionary_entries(), key=lambda e: (e.get("english") or "").lower())
        return render_template("admin_dictionary.html", entries=entries_sorted, token=token, error="Could not read CSV.")

    reader = csv.DictReader(io.StringIO(text))
    # If there's no header, DictReader will treat the first row as header; handle that by falling back.
    has_header = reader.fieldnames and any(name and name.strip().lower() in {"english", "hangul"} for name in reader.fieldnames)
    rows = []
    if has_header:
        rows = list(reader)
    else:
        # Fallback: parse as simple CSV with columns: english,hangul,romanization?,category?
        simple = csv.reader(io.StringIO(text))
        for r in simple:
            if not r or all(not (c or "").strip() for c in r):
                continue
            rows.append({
                "english": r[0] if len(r) > 0 else "",
                "hangul": r[1] if len(r) > 1 else "",
                "romanization": r[2] if len(r) > 2 else "",
                "category": r[3] if len(r) > 3 else "",
            })

    payload = _load_custom_dictionary()
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        entries = []

    now = int(time.time())
    added = 0
    updated = 0
    skipped = 0

    def upsert(eng: str, han: str, rom: str, cat: str):
        nonlocal added, updated, skipped, entries
        eng = (eng or "").strip()
        han = _clean_korean_candidate(han or "")
        rom = (rom or "").strip()
        cat = (cat or "").strip()
        if not eng or not _has_hangul(han):
            skipped += 1
            return

        k = _normalize_english_key(eng)
        for e in entries:
            if not isinstance(e, dict):
                continue
            if _normalize_english_key(e.get("english") or "") == k:
                e["english"] = eng
                e["hangul"] = han
                if rom:
                    e["romanization"] = rom
                else:
                    e.pop("romanization", None)
                if cat:
                    e["category"] = cat
                else:
                    e.pop("category", None)
                e["updated_at"] = now
                updated += 1
                return

        entries.append({
            "english": eng,
            "hangul": han,
            "romanization": rom,
            "category": cat,
            "created_at": now,
            "updated_at": now,
        })
        added += 1

    for r in rows:
        if not isinstance(r, dict):
            continue
        upsert(r.get("english"), r.get("hangul"), r.get("romanization"), r.get("category"))

    payload["schema_version"] = 1
    payload["entries"] = entries
    _save_custom_dictionary(payload)
    try:
        _english_to_hangul_index.cache_clear()
    except Exception:
        pass

    entries_sorted = sorted(_list_custom_dictionary_entries(), key=lambda e: (e.get("english") or "").lower())
    notice = f"Imported: {added} added, {updated} updated, {skipped} skipped."
    return render_template("admin_dictionary.html", entries=entries_sorted, token=token, notice=notice)


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
