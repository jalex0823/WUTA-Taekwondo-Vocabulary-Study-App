# Deployment Guide - WUTA Taekwondo Vocabulary Study App

## Quick Fix for Current Error

The error you're seeing is because:
1. Health check is looking for port **8080**
2. Flask is running on port **5000**
3. You need a production WSGI server (not Flask's dev server)

## Solution: Deploy to Fly.io

### Step 1: Install Fly CLI (if not already installed)
```bash
# macOS
brew install flyctl

# Or via script
curl -L https://fly.io/install.sh | sh
```

### Step 2: Login to Fly.io
```bash
flyctl auth login
```

### Step 3: Launch the App
From your project directory:
```bash
cd /Users/jalex0823/Documents/GitHub/WUTA-Taekwondo-Vocabulary-Study-App

# This will use the existing fly.toml configuration
flyctl launch --no-deploy

# Then deploy
flyctl deploy
```

### Step 4: Monitor the Deployment
```bash
# Watch logs
flyctl logs

# Check status
flyctl status

# Open in browser
flyctl open
```

## What I've Added

### 1. **Dockerfile** ✅
- Uses Python 3.11 slim image
- Installs gunicorn (production WSGI server)
- Exposes port 8080 (not 5000)
- Sets production environment variables

### 2. **fly.toml** ✅
- Fly.io configuration file
- Internal port: 8080
- Health checks configured
- Auto-scaling settings
- Memory: 256MB

### 3. **requirements-prod.txt** ✅
- Gunicorn for production serving

### 4. **Updated app.py** ✅
- Reads PORT from environment variable
- Binds to 0.0.0.0 (allows external connections)
- Disables debug in production

### 5. **.dockerignore** ✅
- Excludes unnecessary files from Docker build

## Alternative: If You're Already Deployed

If you've already created the Fly.io app, just redeploy:

```bash
# Commit the new changes
git add .
git commit -m "Add production deployment configuration"
git push origin main

# Deploy to Fly.io
flyctl deploy
```

## Configuration Details

### Port Configuration
- **Local development**: Port 5000 (default)
- **Production (Fly.io)**: Port 8080
- **Environment variable**: `PORT=8080`

### Gunicorn Settings
- **Workers**: 2 (handles multiple requests)
- **Threads per worker**: 4
- **Timeout**: 120 seconds (for gTTS audio generation)

### Health Checks
- **HTTP check**: `GET /` every 10 seconds
- **TCP check**: Every 15 seconds
- **Grace period**: 5 seconds

## Troubleshooting

### If deployment fails:
```bash
# Check logs
flyctl logs

# Check app status
flyctl status

# SSH into the machine
flyctl ssh console
```

### If health checks fail:
1. Verify port 8080 is exposed in Dockerfile
2. Check that gunicorn is binding to 0.0.0.0:8080
3. Ensure Flask app is responding to GET /

### Test locally with Docker:
```bash
# Build image
docker build -t wuta-app .

# Run container
docker run -p 8080:8080 wuta-app

# Test in browser
open http://localhost:8080
```

## Environment Variables

The app uses these environment variables:

| Variable | Development | Production |
|----------|-------------|------------|
| `PORT` | 5000 | 8080 |
| `FLASK_ENV` | development | production |
| `PYTHONUNBUFFERED` | - | 1 |

## Cost Estimate (Fly.io)

With current configuration:
- **Memory**: 256MB
- **Auto-stop**: Yes (stops when idle)
- **Auto-start**: Yes (starts on request)
- **Cost**: ~$0-5/month (free tier eligible)

## Next Steps

1. **Commit these changes**:
   ```bash
   git add .
   git commit -m "Add production deployment configuration"
   git push origin main
   ```

2. **Deploy to Fly.io**:
   ```bash
   flyctl deploy
   ```

3. **Get your app URL**:
   ```bash
   flyctl info
   # Will show: https://wuta-taekwondo-vocab.fly.dev
   ```

4. **Share with students**! 🥋✨

---

**The health check error will be resolved once you redeploy with these configuration files!**
