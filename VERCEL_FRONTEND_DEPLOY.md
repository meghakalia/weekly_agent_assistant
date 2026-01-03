# Deploy Next.js Frontend to Vercel

## 🚀 Quick Deploy Steps

### 1. Go to Vercel Dashboard
Visit: https://vercel.com/dashboard

### 2. Import Project
- Click **"Add New..."** → **"Project"**
- Select **"Import Git Repository"**
- Choose: `meghakalia/weekly_agent_assistant`
- Click **"Import"**

### 3. Configure Project

**Framework Preset:** Next.js (auto-detected)

**Root Directory:** `inventory-app` ⚠️ **IMPORTANT!**

**Build Settings:**
- Build Command: `npm run build` (default)
- Output Directory: `.next` (default)
- Install Command: `npm install` (default)

### 4. Add Environment Variable

Click "Environment Variables" and add:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://your-render-app.onrender.com` |

**Replace with your actual Render URL!**

Example:
```
NEXT_PUBLIC_API_URL=https://weekly-grocery-agent.onrender.com
```

### 5. Deploy!

Click **"Deploy"**

Wait 2-3 minutes for build to complete.

---

## 📝 What You Need

From your Render deployment, get the URL:
1. Go to https://dashboard.render.com
2. Click your service
3. Copy the URL (e.g., `https://weekly-grocery-agent.onrender.com`)
4. Use this URL for `NEXT_PUBLIC_API_URL` in Vercel

---

## ✅ After Deployment

Your app will be live at: `https://your-project.vercel.app`

**Test it:**
1. Visit your Vercel URL
2. Upload a receipt image
3. Generate shopping list
4. Verify it connects to your Render backend

---

## 🔧 Troubleshooting

### CORS Errors?
Your backend already has CORS enabled in `backend/main.py`:
```python
CORS(app)
```

If you still see CORS errors, update it to:
```python
CORS(app, origins=["https://your-vercel-app.vercel.app"])
```

### Backend Not Connecting?
1. Check `NEXT_PUBLIC_API_URL` is set correctly in Vercel
2. Verify Render backend is running (check /health endpoint)
3. Make sure Render URL is correct (no trailing slash)

### Build Fails?
- Make sure Root Directory is set to `inventory-app`
- Check build logs in Vercel dashboard
- Verify `package.json` has all dependencies

---

## 🎯 Local Testing First

Before deploying, test locally:

```bash
cd inventory-app

# Install dependencies
npm install

# Set environment variable
echo "NEXT_PUBLIC_API_URL=https://your-render-app.onrender.com" > .env.local

# Run dev server
npm run dev
```

Visit http://localhost:3000 and test the connection.

---

## 📱 Your Full Stack Setup

**Frontend (Vercel):**
- Next.js app
- Global CDN
- Auto-deploy on git push
- FREE tier

**Backend (Render):**
- Flask + CrewAI
- Python 3.11
- AI processing
- FREE tier

**Flow:**
```
User → Vercel (Next.js)
       ↓
       → Render (Flask API)
          ↓
          → CrewAI + Gemini AI
             ↓
             → Response back to user
```

---

## 🎉 You're Done!

Once deployed:
✅ Frontend on Vercel
✅ Backend on Render
✅ Full-stack AI grocery app live!

**Share your app URL with the world! 🌍**
