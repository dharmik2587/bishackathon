# Deploy to Vercel (Fast)

## ✅ vercel.json is Required

The `vercel.json` file in the root directory tells Vercel how to build and deploy your project. It's already configured - just commit and push it.

---

## Option 1: Frontend on Vercel + Backend on Render (Recommended - Fastest)

### Step 1: Deploy Frontend to Vercel (2-3 minutes)

**Method A: Automatic (Vercel reads vercel.json)**

1. Go to https://vercel.com/new
2. **Sign in with GitHub** (if not already)
3. **Import Project** → Select `bishackathon` repo
4. Vercel will automatically detect `vercel.json` and configure:
   - ✅ Framework: Vite (auto-detected)
   - ✅ Root Directory: `frontend/` 
   - ✅ Build Command: `cd frontend && npm run build`
   - ✅ Output Directory: `frontend/dist`
5. **Add Environment Variable**:
   ```
   VITE_API_URL = https://bis-rag-backend.onrender.com
   ```
   (Click "Environment Variables" → Add)
6. Click **Deploy** → Done in ~1-2 minutes ✅

**Your frontend is now live at**: `https://bishackathon.vercel.app`

**Method B: Manual (if auto-detect doesn't work)**

1. In Vercel dashboard, click "Edit Project Settings"
2. Override with:
   - **Root Directory**: `frontend/`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Save and trigger redeploy

### Step 2: Deploy Backend to Render (Already Done)

Backend is on Render → `https://bis-rag-backend.onrender.com`

**Total Time**: ~5 minutes for both

---
)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Redirect to FastAPI instance
        pass
```

> **Not recommended** - FastAPI needs continuous process, not serverless

---

## ✨ FASTEST SOLUTION (Recommended)

### Backend: Render (Already Deployed)
```
https://bis-rag-backend.onrender.com
```

### Frontend: Vercel (Deploy Now)
```
https://bishackathon.vercel.app
```

---

## 🚀 Quick Deploy Steps

### 1️⃣ Deploy Frontend to Vercel (2 min)
```
1. Go to https://vercel.com/new
2. Import GitHub repo: dharmik2587/bishackathon
3. Root: frontend/
4. Build: npm run build
5. Output: dist
6. Env: VITE_API_URL=https://bis-rag-backend.onrender.com
7. Click Deploy
```

### 2️⃣ Update render.yaml (Already Done ✅)
- Backend on Render
- Frontend can be on Vercel or Render

### 3️⃣ Test
```
Frontend: https://bishackathon.vercel.app
Backend:  https://bis-rag-backend.onrender.com
```

---

## Alternative: Full Stack on Railway

If you want both on one platform (Railway is free tier friendly):

1. Go to https://railway.app
2. Create new project → GitHub
3. Add `railway.json` (auto-detection)
4. Deploy both backend + frontend
5. Free tier: ~$5/month usage

---

## Alternative: Both on Render (Simplest)

Already configured! Just:
1. Go to https://dashboard.render.com/
2. Click **New → Blueprint**
3. Import `render.yaml`
4. Deploy both services simultaneously

---

## ⚡ Deployment Decision Matrix

| Platform | Frontend | Backend | Cost | Speed | Recommendation |
|----------|----------|---------|------|-------|-----------------|
| **Vercel** | ✅ Excellent | ❌ Serverless | Free | ⚡⚡⚡ Fast | Frontend only |
| **Render** | ✅ Good | ✅ Good | Free | ⚡⚡ Medium | Full stack |
| **Railway** | ✅ Good | ✅ Good | Free tier | ⚡⚡ Medium | Full stack |
| **Fly.io** | ✅ Good | ✅ Good | Free tier | ⚡⚡⚡ Fast | Full stack |

---

## 🎯 Recommended: Vercel + Render

**Frontend**: Vercel (Free, fast CDN, best for static/React)
**Backend**: Render (Free tier, sufficient for API)

**Deploy time**: 5-7 minutes total

---

## Deployment Summary

### ✅ Currently Ready:
- `render.yaml` - Deploy both to Render
- `vercel.json` - Deploy frontend to Vercel only
- `DEPLOY.md` - Complete Render guide

### 🚀 To Deploy Now:

#### Option A (Fastest - Hybrid):
1. Frontend → Vercel (https://vercel.com/new)
2. Backend → Render (https://render.com/blueprints)
3. Total time: ~10 minutes

#### Option B (Simplest - Single Platform):
1. Both → Render (https://render.com/blueprints)
2. Use `render.yaml`
3. Total time: ~5 minutes

---

## Environment Variables Needed

### For Render Backend:
```
ANTHROPIC_API_KEY = your_anthropic_api_key
PORT = 8000
```

### For Vercel Frontend:
```
VITE_API_URL = https://bis-rag-backend.onrender.com
```

---

## Post-Deployment Checklist

- [ ] Frontend loads at Vercel URL
- [ ] Backend responds at Render API URL
- [ ] Search works end-to-end
- [ ] Evaluation runs successfully
- [ ] No CORS errors in browser console

---

## Commands for Local Testing

```bash
# Backend (Terminal 1)
cd "d:\opencode\BIS RAG"
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000

# Frontend (Terminal 2)
cd frontend
npm run dev
```

Access at: http://localhost:5173

---

## Troubleshooting

### Frontend Can't Connect to Backend
```
Error: CORS / Failed to fetch
Solution: Check VITE_API_URL env var matches backend URL
```

### Backend Error on Render
```
Solution: Check logs in Render dashboard
Ensure ANTHROPIC_API_KEY is set correctly
```

### Vercel Build Fails
```
Solution: 
- Clear build cache: Vercel dashboard → Settings → Git
- Verify frontend/package.json exists
- Check build command
```

---

## Quick Links

- **Vercel Dashboard**: https://vercel.com/dashboard
- **Render Dashboard**: https://dashboard.render.com/
- **GitHub Repo**: https://github.com/dharmik2587/bishackathon
- **Backend API**: https://bis-rag-backend.onrender.com/api/results
- **Frontend**: https://bishackathon.vercel.app

---

## Next Steps

1. **Choose deployment option** (Vercel + Render recommended)
2. **Set environment variables**
3. **Click deploy**
4. **Test the live application**
5. **Share the URLs!**

🎉 That's it! Your BIS RAG engine is now live on the internet.
