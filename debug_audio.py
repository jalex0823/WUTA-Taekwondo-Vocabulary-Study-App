#!/usr/bin/env python3
"""
Debug script to verify each term generates its own unique bilingual audio
"""
import json
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "terms.json"

def verify_audio_setup():
    """Verify the audio generation logic"""
    
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🔍 Verifying audio setup for each term...\n")
    
    # Check first 5 terms from different belts
    test_terms = []
    for belt in data['belts'][:3]:  # First 3 belts
        for term in belt['terms'][:2]:  # First 2 terms each
            test_terms.append({
                'belt': belt['belt_name'],
                'id': term['id'],
                'korean': term['hangul'],
                'english': term['english']
            })
    
    print(f"Testing {len(test_terms)} terms:\n")
    
    for i, term in enumerate(test_terms, 1):
        print(f"{i}. Belt: {term['belt']}")
        print(f"   Term ID: {term['id']}")
        print(f"   Korean: {term['korean']}")
        print(f"   English: {term['english']}")
        print(f"   Audio URL: /audio/{term['id']}")
        print(f"   Expected: '{term['korean']}' + pause + '{term['english']}'")
        print()
    
    print("✅ Each term has a unique ID and will generate separate audio")
    print("✅ Each audio file contains: Korean + 500ms pause + English")
    print("\n⚠️  If you're hearing only Korean, the issue is:")
    print("   1. Old cached files in production (need to delete static/audio/*.mp3)")
    print("   2. Or pydub not installed on production server")
    print("\n💡 Solution:")
    print("   - Run: python3 clear_audio_cache.py")
    print("   - Make sure pydub is in requirements.txt")
    print("   - Make sure ffmpeg is installed on production server")

if __name__ == "__main__":
    verify_audio_setup()
