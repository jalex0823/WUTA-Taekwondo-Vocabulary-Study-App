#!/usr/bin/env python3
"""Test that audio generation produces bilingual (Korean + English) files"""

from gtts import gTTS
from pydub import AudioSegment
import io
import os

print("🧪 Testing Bilingual Audio Generation\n")

# Test data
test_term = {
    "hangul": "태권도",
    "english": "The Way of Hand and Foot"
}

try:
    print(f"Generating audio for: {test_term['hangul']} = {test_term['english']}")
    
    # Create Korean audio
    korean_tts = gTTS(text=test_term["hangul"], lang='ko', slow=True)
    korean_audio_bytes = io.BytesIO()
    korean_tts.write_to_fp(korean_audio_bytes)
    korean_audio_bytes.seek(0)
    print("✅ Korean audio generated")
    
    # Create English audio
    english_tts = gTTS(text=test_term["english"], lang='en', slow=True)
    english_audio_bytes = io.BytesIO()
    english_tts.write_to_fp(english_audio_bytes)
    english_audio_bytes.seek(0)
    print("✅ English audio generated")
    
    # Combine with pydub
    korean_audio = AudioSegment.from_mp3(korean_audio_bytes)
    english_audio = AudioSegment.from_mp3(english_audio_bytes)
    pause = AudioSegment.silent(duration=500)
    
    combined = korean_audio + pause + english_audio
    print("✅ Combined: Korean + 500ms pause + English")
    
    # Save test file
    output_path = "static/audio/test_bilingual.mp3"
    os.makedirs("static/audio", exist_ok=True)
    combined.export(output_path, format="mp3")
    
    # Check file size
    file_size = os.path.getsize(output_path)
    print(f"✅ Saved to: {output_path}")
    print(f"✅ File size: {file_size} bytes")
    
    if file_size > 5000:
        print("\n✅ SUCCESS! Bilingual audio works correctly!")
        print(f"   Korean-only would be ~3000 bytes")
        print(f"   Bilingual is {file_size} bytes - includes both languages!")
    else:
        print(f"\n⚠️  Warning: File seems small ({file_size} bytes)")
    
    print(f"\n🎵 Test the audio: open http://127.0.0.1:5000/audio/test_bilingual.mp3")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nMake sure you have installed:")
    print("  pip3 install gTTS pydub")
    print("  brew install ffmpeg")
