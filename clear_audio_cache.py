#!/usr/bin/env python3
"""
Clear all cached audio files to force regeneration with bilingual (Korean + English) format
"""
import os
from pathlib import Path

AUDIO_DIR = Path(__file__).parent / "static" / "audio"

def clear_audio_cache():
    """Remove all MP3 files from the audio directory (except sfx folder)"""
    if not AUDIO_DIR.exists():
        print("Audio directory doesn't exist yet")
        return
    
    count = 0
    for audio_file in AUDIO_DIR.glob("*.mp3"):
        try:
            audio_file.unlink()
            count += 1
            print(f"✓ Deleted: {audio_file.name}")
        except Exception as e:
            print(f"✗ Error deleting {audio_file.name}: {e}")
    
    print(f"\n✅ Cleared {count} audio files")
    print("🔄 Audio files will regenerate with Korean + English when accessed")

if __name__ == "__main__":
    print("🗑️  Clearing old audio cache...")
    clear_audio_cache()
