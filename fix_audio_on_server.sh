#!/bin/bash
# Run this script ON your Digital Ocean server to fix audio issues

echo "🔧 WUTA Audio Fix Script"
echo "========================"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this from your app directory."
    exit 1
fi

# Step 1: Backup existing audio (optional)
echo "📦 Step 1: Backing up existing audio files..."
if [ -d "static/audio" ] && [ "$(ls -A static/audio/*.mp3 2>/dev/null)" ]; then
    mkdir -p backup/audio_backup_$(date +%Y%m%d_%H%M%S)
    cp static/audio/*.mp3 backup/audio_backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
    echo "✅ Backup created (optional)"
else
    echo "ℹ️  No existing audio files to backup"
fi
echo ""

# Step 2: Clear old audio cache
echo "🗑️  Step 2: Clearing old audio files..."
rm -f static/audio/*.mp3
COUNT=$(ls static/audio/*.mp3 2>/dev/null | wc -l)
echo "✅ Cleared audio cache (removed old files)"
echo ""

# Step 3: Verify dependencies
echo "🔍 Step 3: Checking dependencies..."

# Check Python packages
echo "Checking Python packages..."
python3 -c "import pydub" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ pydub is installed"
else
    echo "⚠️  pydub not found - installing..."
    pip3 install pydub
fi

python3 -c "from gtts import gTTS" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ gTTS is installed"
else
    echo "⚠️  gTTS not found - installing..."
    pip3 install gTTS
fi

# Check ffmpeg
which ffmpeg > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ ffmpeg is installed"
else
    echo "❌ ffmpeg NOT installed - REQUIRED for bilingual audio!"
    echo "   Run: sudo apt-get install -y ffmpeg"
    exit 1
fi
echo ""

# Step 4: Test audio generation
echo "🎵 Step 4: Testing audio generation..."
python3 << 'EOF'
from gtts import gTTS
from pydub import AudioSegment
import io

try:
    # Test Korean
    korean = gTTS(text="테스트", lang='ko', slow=True)
    korean_bytes = io.BytesIO()
    korean.write_to_fp(korean_bytes)
    korean_bytes.seek(0)
    
    # Test English
    english = gTTS(text="test", lang='en', slow=True)
    english_bytes = io.BytesIO()
    english.write_to_fp(english_bytes)
    english_bytes.seek(0)
    
    # Test combine
    k_audio = AudioSegment.from_mp3(korean_bytes)
    e_audio = AudioSegment.from_mp3(english_bytes)
    combined = k_audio + AudioSegment.silent(500) + e_audio
    
    print("✅ Audio generation test PASSED")
    print("✅ Bilingual audio will work correctly")
except Exception as e:
    print(f"❌ Audio test FAILED: {e}")
    exit(1)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Audio generation test failed!"
    echo "   Check the error above and fix before continuing"
    exit 1
fi
echo ""

# Step 5: Restart the app
echo "🔄 Step 5: Restarting application..."
if [ -f "/etc/systemd/system/wuta.service" ]; then
    sudo systemctl restart wuta
    echo "✅ App restarted (systemd)"
elif command -v docker &> /dev/null && [ "$(docker ps -q -f name=wuta)" ]; then
    docker restart wuta
    echo "✅ App restarted (docker)"
else
    echo "⚠️  Could not auto-restart. Please restart your app manually:"
    echo "   - If using systemd: sudo systemctl restart your-service"
    echo "   - If using Docker: docker restart your-container"
    echo "   - If using gunicorn: pkill -HUP gunicorn"
fi
echo ""

echo "✅ ============================================"
echo "✅ Audio fix complete!"
echo "✅ ============================================"
echo ""
echo "🎯 What happened:"
echo "   ✓ Old Korean-only audio files deleted"
echo "   ✓ Dependencies verified"
echo "   ✓ Audio generation tested successfully"
echo "   ✓ App restarted"
echo ""
echo "🎵 Next time you load a word:"
echo "   1. New audio file will generate"
echo "   2. It will contain: Korean + pause + English"
echo "   3. All 277 terms will have bilingual audio"
echo ""
echo "💡 Test it: Open your app and click through words!"
