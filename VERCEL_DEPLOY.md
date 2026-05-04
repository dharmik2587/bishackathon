# Deploy to Vercel (Fast)

## Option 1: Frontend on Vercel + Backend on Render (Recommended - Fastest)

### Step 1: Deploy Frontend to Vercel (5 minutes)

1. Go to https://vercel.com/new
2. **Sign in with GitHub** (if not already)
3. **Import Project** → Select `bishackathon` repo
4. **Framework Preset**: Vite
5. **Root Directory**: `frontend/`
6. **Build Command**: `npm run build`
7. **Output Directory**: `dist`
8. **Environment Variables**:
   ```
   VITE_API_URL = https://bis-rag-backend.onrender.com
   ```
9. Click **Deploy** → Done in ~2 minutes ✅

**Your frontend is now live at**: `https://bishackathon.vercel.app`

### Step 2: Deploy Backend to Render (Already Done)

Backend is on Render → `https://bis-rag-backend.onrender.com`

**Total Time**: ~7 minutes for both

---

## Option 2: Serverless Backend on Vercel (Advanced)

> ⚠️ Requires converting FastAPI to Vercel Functions (more complex, but free tier works)

### Step 1: Create Vercel Python Function for Backend

Create `api/query.py`:
```python
from http.server import BaseHTTPRequestHandler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
