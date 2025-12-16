#!/usr/bin/env python3
"""
Clear all cached audio files to force regeneration with bilingual (Korean + English) format
"""
import os
from pathlib import Path

AUDIO_DIR = Path(__file__).parent / "static" / "audio"


def _is_sfx_path(path: Path) -> bool:
    return "sfx" in path.parts

def clear_audio_cache():
    """Remove cached term audio from the audio directory (preserve sfx folder)."""
    if not AUDIO_DIR.exists():
        print("Audio directory doesn't exist yet")
        return
    
    deleted = 0
    skipped = 0

    # Delete cached term MP3s (root + subfolders) but keep any SFX.
    for audio_file in AUDIO_DIR.rglob("*.mp3"):
        if _is_sfx_path(audio_file):
            skipped += 1
            continue
        try:
            audio_file.unlink()
            deleted += 1
            print(f"✓ Deleted: {audio_file.name}")
        except Exception as e:
            print(f"✗ Error deleting {audio_file.name}: {e}")

    # Delete sidecar metadata created by the app (bilingual/korean_only markers)
    for meta_file in AUDIO_DIR.rglob("*.meta.json"):
        if _is_sfx_path(meta_file):
            skipped += 1
            continue
        try:
            meta_file.unlink()
            deleted += 1
            print(f"✓ Deleted: {meta_file.name}")
        except Exception as e:
            print(f"✗ Error deleting {meta_file.name}: {e}")

    # Clean up any temp/partial outputs if present
    for tmp_file in list(AUDIO_DIR.rglob("*.tmp")) + list(AUDIO_DIR.rglob("*.part")):
        if _is_sfx_path(tmp_file):
            skipped += 1
            continue
        try:
            tmp_file.unlink()
            deleted += 1
            print(f"✓ Deleted: {tmp_file.name}")
        except Exception as e:
            print(f"✗ Error deleting {tmp_file.name}: {e}")
    
    print(f"\n✅ Cleared {deleted} cached audio/metadata files")
    if skipped:
        print(f"ℹ️  Skipped {skipped} file(s) in sfx/")
    print("🔄 Audio files will regenerate with Korean + English when accessed")

if __name__ == "__main__":
    print("🗑️  Clearing old audio cache...")
    clear_audio_cache()
