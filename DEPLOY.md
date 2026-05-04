# Deployment Guide: BIS RAG to Render

## Overview
This full-stack application consists of:
- **Backend**: FastAPI service running on port 8000
- **Frontend**: React/Vite application running on port 3000

Both services are defined in `render.yaml` and can be deployed to Render as two separate web services.

## Prerequisites
1. **GitHub account** with your repo: https://github.com/dharmik2587/bishackathon
2. **Render account**: https://render.com
3. Environment variables ready (see below)

## Step 1: Prepare Environment Variables

### Backend Service
- `ANTHROPIC_API_KEY`: Your Anthropic API key (for LLM-powered query rewriting)

### Frontend Service
- `VITE_API_URL`: Backend URL (will be auto-set during deployment, e.g., `https://bis-rag-backend.onrender.com`)

## Step 2: Deploy to Render

### Option A: Using render.yaml (Recommended)

1. Go to https://dashboard.render.com/
2. Click **New → Blueprint**
3. Connect your GitHub repo (dharmik2587/bishackathon)
4. Render will auto-detect `render.yaml`
5. Configure environment variables:
   - Set `ANTHROPIC_API_KEY` for the backend service
6. Click **Deploy**

### Option B: Manual Deployment

#### Deploy Backend:
1. New → Web Service
2. Connect GitHub repo
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `uvicorn backend.api:app --host 0.0.0.0 --port 8000`
5. Add environment variable: `ANTHROPIC_API_KEY`
6. Click Deploy

#### Deploy Frontend:
1. New → Web Service
2. Connect GitHub repo
3. Set build command: `cd frontend && npm install && npm run build`
4. Set start command: `cd frontend && npm run preview -- --host 0.0.0.0 --port 3000`
5. Add environment variable: `VITE_API_URL` = `https://bis-rag-backend.onrender.com` (replace with your backend URL)
6. Click Deploy

## Step 3: Verify Deployment

Once deployed:

1. **Backend**: Visit `https://bis-rag-backend.onrender.com/api/results` (should return JSON)
2. **Frontend**: Visit `https://bis-rag-frontend.onrender.com` (should load the UI)
3. **Search Demo**: Test the search functionality
4. **Evaluation**: Run the evaluation pipeline

## Service URLs (After Deployment)

```
Backend API:  https://bis-rag-backend.onrender.com
Frontend UI:  https://bis-rag-frontend.onrender.com
```

## Local Testing Before Deploy

To test locally before pushing to Render:

```bash
# Terminal 1: Backend
cd "d:\opencode\BIS RAG"
python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Then open `http://127.0.0.1:5173`

## Troubleshooting

### Backend won't start
- Check `ANTHROPIC_API_KEY` is set correctly
- Verify `backend/requirements.txt` has all dependencies
- Check logs: Render dashboard → Service → Logs

### Frontend can't connect to backend
- Ensure `VITE_API_URL` is set to correct backend URL
- Check CORS headers in `backend/api.py`
- Verify backend is running and accessible

### Build fails
- Clear build cache: Render dashboard → Service → Settings → Clear Build Cache
- Verify `requirements.txt` dependencies are compatible
- Check `package.json` scripts exist

## File Structure for Render
```
BIS RAG/
├── render.yaml              ← Render deployment config
├── backend/
│   ├── api.py              ← FastAPI app
│   ├── inference.py        ← BIS retrieval engine
│   └── requirements.txt     ← Python dependencies
└── frontend/
    ├── package.json        ← Node dependencies
    ├── vite.config.ts      ← Vite config
    └── src/                ← React components
```

## CI/CD Pipeline
Once deployed:
- Push changes to `main` branch on GitHub
- Render auto-detects changes via webhook
- Services automatically rebuild and redeploy

## Monitoring

In Render Dashboard:
- **Logs**: Real-time service logs
- **Metrics**: CPU, memory, requests
- **Deploys**: Deployment history
- **Environment**: Current env variables

## Scaling & Optimization

For production:
- Consider using background workers for long-running evaluations
- Enable caching for frequently accessed standards
- Monitor API rate limits
- Set up custom domain (optional)

---

For questions, refer to:
- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- Vite Docs: https://vitejs.dev
