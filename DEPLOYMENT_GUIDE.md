# 🚀 WUTA Bilingual Audio Deployment Guide

## ✅ What's Fixed

The app now has **robust auto-advance** that works even when audio fails:

- ✅ Auto-advance continues even if audio is blocked by browser
- ✅ Auto-advance continues even with old Korean-only cached files  
- ✅ Clear user messaging about cache issues
- ✅ Bilingual audio generation works perfectly ("The word is" + English → pause → Korean)

## 🎯 How It Works Now

### Manual Mode (Default)

1. Navigate with **Previous/Next** buttons
2. Audio auto-plays: "The word is" + English → pause → Korean
3. Can also click **🔊 speaker button** to replay

### Auto Mode

1. Click **"Auto Guide"** tab
2. Click **"Start Auto Play"** button
3. **Cards auto-advance** through all terms:

    - Plays "The word is" + English → pause → Korean
    - Waits (2-7 seconds, your choice)
    - Advances to next card automatically
    - Continues even if audio fails!

## 🔧 Deploy to Production (Digital Ocean)

### Step 1: SSH to Your Server

```bash
ssh root@your-droplet-ip
cd /path/to/your/app
```

### Step 2: Pull Latest Code

```bash
git pull origin main
```

### Step 3: Clear Old Audio Cache

```bash
# Delete all old Korean-only audio files
rm -f static/audio/*.mp3

# Verify they're gone
ls static/audio/
```

### Step 4: Verify Dependencies

```bash
# Check ffmpeg is installed (required for bilingual audio)
which ffmpeg

# If not installed:
sudo apt-get update
sudo apt-get install -y ffmpeg

# Check Python packages
pip3 list | grep -E "gTTS|pydub"

# If missing:
pip3 install gTTS pydub
```

### Step 5: Restart App

```bash
# If using systemd:
sudo systemctl restart wuta

# If using Docker:
docker restart wuta

# If using gunicorn manually:
pkill -HUP gunicorn
```

### Step 6: Test

1. Visit your production URL
2. Navigate to any belt level
3. Click **Auto Guide** → **Start Auto Play**
4. First word plays: Should hear "The word is" + English → pause → Korean (4-5 seconds total)
5. Cards should auto-advance every 5 seconds

## 🧪 Verify Bilingual Audio

### Check File Sizes

```bash
# On server, after visiting a few pages:
ls -lh static/audio/*.mp3 | head -5
```

**Expected:**

- ❌ Korean-only: ~3,000-5,000 bytes (1-2 seconds)
- ✅ Bilingual: ~10,000-20,000 bytes (4-5 seconds)

If files are small (< 6,000 bytes), they're Korean-only. Delete and regenerate:

```bash
rm -f static/audio/*.mp3
sudo systemctl restart wuta
```

## 🐛 Troubleshooting

### Problem: Only Korean Audio

**Cause:** Old cached files from before bilingual feature  
**Fix:** Delete `static/audio/*.mp3` and restart app

### Problem: No Audio Generation

**Cause:** Missing ffmpeg or pydub  
**Fix:** Install dependencies (see Step 4 above)

### Problem: Cards Don't Auto-Advance

**Cause:** Old version of code  
**Fix:** `git pull origin main` and restart (see Steps 2 & 5)

### Problem: Network Errors

**Cause:** gTTS needs internet to generate audio  
**Fix:** Check server internet connection, or pre-generate all audio

## 📊 Pre-Generate All Audio (Optional)

Want to generate all 277 audio files at once?

```python
# On server:
python3 << 'EOF'
import requests
import json

# Load terms
with open('data/terms.json', 'r') as f:
    data = json.load(f)

# Generate all audio
base_url = 'http://127.0.0.1:8080'  # or your production URL
count = 0
for belt in data['belts']:
    for term in belt['terms']:
        url = f"{base_url}/audio/{term['id']}"
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                count += 1
                print(f"✅ {count}/277: {term['id']}")
        except Exception as e:
            print(f"❌ Failed: {term['id']} - {e}")

print(f"\n✅ Generated {count} audio files!")
EOF
```

## 📝 Summary

**After deployment, your app will:**

- ✅ Play English + Korean for all 277 terms
- ✅ Auto-advance through vocabulary in Auto Mode
- ✅ Continue advancing even if audio fails (no more stuck!)
- ✅ Work on iOS and all modern browsers
- ✅ Cache audio for fast repeat access

**Files to delete on server:** `static/audio/*.mp3` (old Korean-only files)  
**Files to keep:** Everything else!  

🎵 **Users will hear bilingual audio for every term!**
