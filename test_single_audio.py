#!/usr/bin/env python3
"""Test single audio file generation to verify bilingual works"""

from gtts import gTTS
from pydub import AudioSegment
import io
import os

# Test term
hangul = "태권도"
english = "The Way of Hand and Foot"

print(f"Testing: {hangul} = {english}\n")

try:
    # Create Korean audio
    print("1. Generating Korean audio...")
    korean_tts = gTTS(text=hangul, lang='ko', slow=True)
    korean_audio_bytes = io.BytesIO()
    korean_tts.write_to_fp(korean_audio_bytes)
    korean_audio_bytes.seek(0)
    korean_size = len(korean_audio_bytes.getvalue())
    print(f"   ✅ Korean: {korean_size} bytes")
    
    # Create English audio
    print("2. Generating English audio...")
    english_tts = gTTS(text=english, lang='en', slow=True)
    english_audio_bytes = io.BytesIO()
    english_tts.write_to_fp(english_audio_bytes)
    english_audio_bytes.seek(0)
    english_size = len(english_audio_bytes.getvalue())
    print(f"   ✅ English: {english_size} bytes")
    
    # Combine
    print("3. Combining audio...")
    korean_audio = AudioSegment.from_mp3(korean_audio_bytes)
    english_audio = AudioSegment.from_mp3(english_audio_bytes)
    pause = AudioSegment.silent(duration=500)
    
    combined = korean_audio + pause + english_audio
    
    # Save
    output_path = "static/audio/test_direct.mp3"
    os.makedirs("static/audio", exist_ok=True)
    combined.export(output_path, format="mp3")
    
    final_size = os.path.getsize(output_path)
    print(f"   ✅ Combined: {final_size} bytes")
    
    print(f"\n✅ SUCCESS!")
    print(f"   Korean only would be: ~{korean_size} bytes")
    print(f"   Bilingual is: {final_size} bytes")
    print(f"   File is {final_size / korean_size:.1f}x larger = includes English!")
    print(f"\n🎵 Play the file: {output_path}")
    
    # Show duration
    print(f"\n⏱️  Duration:")
    print(f"   Korean: {len(korean_audio)/1000:.1f} seconds")
    print(f"   Pause: 0.5 seconds")
    print(f"   English: {len(english_audio)/1000:.1f} seconds")
    print(f"   Total: {len(combined)/1000:.1f} seconds")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
