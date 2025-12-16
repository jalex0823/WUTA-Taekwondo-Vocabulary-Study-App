# Quick Deployment Commands

## To Fix Your Current Health Check Error:

Run this command in your terminal to redeploy with the fixed configuration:

```bash
cd /Users/jalex0823/Documents/GitHub/WUTA-Taekwondo-Vocabulary-Study-App
flyctl deploy
```

That's it! The new deployment will:
- ✅ Use port 8080 (matching health checks)
- ✅ Run gunicorn (production server)
- ✅ Pass all health checks
- ✅ Auto-scale based on traffic

## Monitor Deployment:

```bash
# Watch deployment progress
flyctl logs

# Check when it's ready
flyctl status

# Open in browser once deployed
flyctl open
```

## Expected Output:

You should see:
```
==> Monitoring deployment
...
✓ Successfully deployed!
✓ Health checks passing
```

Then you can access your app at: **https://wuta-taekwondo-vocab.fly.dev**

---

**The health check error will be resolved immediately after redeploying!** 🚀
