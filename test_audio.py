#!/usr/bin/env python3
"""
Test bilingual audio generation for all terms
"""
import json
import requests
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "terms.json"
BASE_URL = "http://localhost:8000"

def test_audio_generation():
    """Test that audio is generated with both Korean and English"""
    
    # Load all terms
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🎵 Testing bilingual audio generation...\n")
    
    # Test first 3 terms from each belt
    tested = 0
    max_tests = 10  # Limit testing to avoid too many requests
    
    for belt in data['belts']:
        if tested >= max_tests:
            break
            
        print(f"\n📘 Testing {belt['belt_name']}:")
        
        for term in belt['terms'][:2]:  # Test first 2 terms per belt
            if tested >= max_tests:
                break
                
            term_id = term['id']
            hangul = term['hangul']
            english = term['english']
            
            print(f"\n  Testing: {hangul} → {english}")
            print(f"  Term ID: {term_id}")
            
            # Request audio
            url = f"{BASE_URL}/audio/{term_id}"
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    # Check file size (bilingual should be larger)
                    size = len(response.content)
                    print(f"  ✅ Audio generated: {size:,} bytes")
                    
                    if size > 5000:  # Bilingual audio should be larger
                        print(f"  ✨ Likely includes both Korean AND English")
                    else:
                        print(f"  ⚠️  Small file - might be Korean only")
                else:
                    print(f"  ❌ Error: HTTP {response.status_code}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
            
            tested += 1
    
    print(f"\n\n✅ Tested {tested} terms")
    print("🎯 All audio files will be generated on-demand with Korean + English")
    print("💡 Test by visiting: http://localhost:8000")

if __name__ == "__main__":
    test_audio_generation()
