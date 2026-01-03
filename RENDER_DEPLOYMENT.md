# Weekly Grocery Agent - Render Deployment Guide

## 🚀 Deploy to Render in 5 Minutes

### Prerequisites
- ✅ Render account (already logged in)
- ✅ GitHub repository
- ✅ API keys (Gemini/Google AI)

---

## Step 1: Push Code to GitHub

First, commit and push all changes:

```bash
git add .
git commit -m "Add Render deployment config"
git push origin vercel-deployment
```

---

## Step 2: Create New Web Service on Render

1. **Go to Render Dashboard**: [dashboard.render.com](https://dashboard.render.com)

2. **Click "New +"** → Select **"Web Service"**

3. **Connect Repository**:
   - Click "Connect GitHub" (if not already connected)
   - Find and select: `meghakalia/weekly_agent_assistant`
   - Click "Connect"

4. **Configure Service**:
   
   | Setting | Value |
   |---------|-------|
   | **Name** | `weekly-grocery-agent` |
   | **Region** | Oregon (US West) or nearest to you |
   | **Branch** | `vercel-deployment` |
   | **Root Directory** | Leave blank (uses project root) |
   | **Environment** | `Python 3` |
   | **Build Command** | `./build.sh` |
   | **Start Command** | `gunicorn backend.main:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1 --log-level info` |
   | **Plan** | **Free** |

---

## Step 3: Add Environment Variables

Scroll down to **"Environment Variables"** section and add:

### Required Variables:

```bash
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### Optional but Recommended:

```bash
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
OPENAI_API_KEY=your_openai_api_key_here (if using OpenAI)
OUTPUT_DIR=/tmp/outputs
PORT=8080
PYTHONUNBUFFERED=1
```

**Important**: Get your Gemini API key from: https://makersuite.google.com/app/apikey

---

## Step 4: Deploy!

1. Click **"Create Web Service"** at the bottom

2. Watch the build logs:
   - Installing dependencies (~2-3 minutes)
   - Building application
   - Starting server

3. Wait for **"Live"** status (green indicator)

---

## Step 5: Test Your Deployment

Once deployed, your service will be at: `https://weekly-grocery-agent.onrender.com`

### Test the health endpoint:

```bash
curl https://your-app-name.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-02T...",
  "service": "Weekly Grocery Agent API",
  "version": "1.0.0"
}
```

### Available Endpoints:

- `GET /` - API info
- `GET /health` - Health check
- `POST /api/process-inventory` - Upload receipt image
- `POST /api/generate-shopping-list` - Generate shopping list

---

## Step 6: Update Frontend (if using separate frontend)

If you're deploying frontend separately (e.g., on Vercel), update the API URL:

In `inventory-app/app/config.ts` or where you define API endpoints:

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://your-app-name.onrender.com';
```

Then set environment variable in Vercel:
```bash
NEXT_PUBLIC_API_URL=https://your-app-name.onrender.com
```

---

## 📊 Understanding Render Free Tier

### What You Get:
- ✅ 512MB RAM
- ✅ Shared CPU
- ✅ 750 hours/month (essentially unlimited)
- ✅ Automatic HTTPS
- ✅ Auto-deploy on git push
- ✅ Free forever (no credit card required)

### Limitations:
- ⚠️ **Spins down after 15 min of inactivity**
  - First request after sleep takes ~30-50 seconds to wake up
  - Subsequent requests are fast
- ⚠️ Shared resources (may be slower during peak times)

### Tips to Handle Sleep:
1. Use a cron job to ping your app every 14 minutes (keeps it awake)
2. Show loading message to users: "Waking up server, please wait..."
3. Upgrade to paid plan ($7/mo) for always-on service

---

## 🔧 Troubleshooting

### Build Fails?

**Check Python version:**
- Render uses Python 3.11 by default
- Your app should be compatible

**Check dependencies:**
- All dependencies are in `requirements.txt`
- CrewAI installs correctly

**View logs:**
- Click on your service
- Go to "Logs" tab
- Look for red error messages

### App Crashes After Deploy?

**Check environment variables:**
- Ensure `GEMINI_API_KEY` is set correctly
- No typos in variable names

**Check start command:**
- Should be: `gunicorn backend.main:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1`
- Port must be `$PORT` (Render sets this automatically)

### Timeout Errors?

If CrewAI processing takes too long:
- Increase `--timeout 300` in start command (max ~600 seconds on free tier)
- Consider optimizing your AI prompts
- Free tier should handle most requests

### Import Errors?

If you see "ModuleNotFoundError":
- Check that `build.sh` runs successfully
- Verify all dependencies in `requirements.txt`
- Check `PYTHONPATH` settings

---

## 🎯 Post-Deployment Checklist

- [ ] Service shows "Live" status (green)
- [ ] Health endpoint returns 200 OK
- [ ] Can upload and process receipt images
- [ ] Shopping list generation works
- [ ] No errors in logs
- [ ] Frontend connects to backend (if separate)

---

## 📈 Monitoring Your App

### View Logs:
1. Go to Render Dashboard
2. Click your service
3. Click "Logs" tab
4. See real-time logs

### View Metrics:
1. Click "Metrics" tab
2. See CPU, memory usage
3. Monitor response times

### Auto-Deploy:
- Every git push to `vercel-deployment` branch triggers automatic deployment
- Watch logs to ensure successful deployment

---

## 💰 Upgrading (Optional)

If you need:
- ❌ No sleep (always on)
- ❌ More RAM (1GB+)
- ❌ Priority support

Upgrade to **Starter Plan ($7/month)**:
1. Go to service settings
2. Click "Upgrade"
3. Select Starter plan

---

## 🆘 Need Help?

**Render Support:**
- [Render Docs](https://render.com/docs)
- [Community Forum](https://community.render.com)
- [Status Page](https://status.render.com)

**Common Issues:**
- App sleeps: Normal on free tier, add keep-alive ping
- Slow first request: Wake-up time, expected behavior
- Build fails: Check logs for specific errors

---

## ✅ Success!

Your app is now live at: **https://your-app-name.onrender.com**

Test it:
```bash
curl https://your-app-name.onrender.com/health
```

🎉 Congratulations! Your Weekly Grocery Agent is deployed!
