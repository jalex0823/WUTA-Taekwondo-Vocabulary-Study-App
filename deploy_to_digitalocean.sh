#!/bin/bash
# Deploy script to Digital Ocean with audio cache clearing

echo "🚀 Deploying WUTA Taekwondo App to Digital Ocean..."
echo ""

# Step 1: SSH into Digital Ocean and clear audio cache
echo "📝 Step 1: Clearing old audio cache on server..."
echo "Run this command on your Digital Ocean droplet:"
echo ""
echo "ssh your-droplet-ip"
echo "cd /path/to/your/app"
echo "rm -f static/audio/*.mp3"
echo "echo 'Cleared audio cache'"
echo ""

# Step 2: Push to GitHub
echo "📝 Step 2: Pushing latest code to GitHub..."
git add .
git commit -m "Fix: Clear audio cache for bilingual regeneration"
git push origin main
echo "✅ Code pushed to GitHub"
echo ""

# Step 3: Pull on server
echo "📝 Step 3: Pull latest code on server..."
echo "Run this command on your Digital Ocean droplet:"
echo ""
echo "ssh your-droplet-ip"
echo "cd /path/to/your/app"
echo "git pull origin main"
echo "sudo systemctl restart your-app-service"
echo ""

echo "✅ Deployment instructions complete!"
echo ""
echo "🎯 What this does:"
echo "   1. Deletes all old audio files (Korean-only)"
echo "   2. Updates code to latest version"
echo "   3. Restarts the app"
echo "   4. New audio files will regenerate with Korean + English"
echo ""
echo "📌 Important: Make sure ffmpeg is installed on your server!"
echo "   Run: sudo apt-get install -y ffmpeg"
