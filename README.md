# BIS Standards RAG Engine v7.0

A high-performance **Retrieval-Augmented Generation (RAG)** engine for the **Bureau of Indian Standards (BIS)**, built on a three-stage hybrid retrieval architecture — BM25 lexical search, dense semantic embeddings, and cross-encoder re-ranking — delivering **>95% Hit@3** and **<3s latency** on 570+ standards.

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER / FRONTEND                          │
│  React + TypeScript + GSAP + Tailwind CSS (Vite dev server)     │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────────┐   │
│  │  Search Demo │  │ Eval Dashboard   │  │  Pipeline Viz     │   │
│  │  POST /query │  │ POST /evaluate   │  │  (Architecture)   │   │
│  └──────┬──────┘  └────────┬─────────┘  └───────────────────┘   │
└─────────┼──────────────────┼────────────────────────────────────┘
          │ HTTP             │ HTTP
          ▼                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND (api.py)                       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              BISRetrievalEngine (inference.py)              │  │
│  │                                                            │  │
│  │  ┌──────────┐   ┌──────────────┐   ┌───────────────────┐  │  │
│  │  │  BM25    │   │  Dense       │   │  Cross-Encoder    │  │  │
│  │  │  Lexical │──▶│  Semantic    │──▶│  Re-Ranking       │  │  │
│  │  │  Search  │   │  Retrieval   │   │  (Final Top-K)    │  │  │
│  │  └──────────┘   └──────────────┘   └───────────────────┘  │  │
│  │       ▲               ▲                     ▲              │  │
│  │       │               │                     │              │  │
│  │  rank_bm25       all-MiniLM         ms-marco-TinyBERT     │  │
│  │  (Okapi)         L6-v2              L-2-v2                │  │
│  └────────────────────────────────────────────────────────────┘  │
│                          ▲                                       │
│                          │                                       │
│              ┌───────────┴───────────┐                           │
│              │  standards_enriched   │                           │
│              │  .json (570+ stds)    │                           │
│              └───────────────────────┘                           │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Detailed Retrieval Pipeline

### Stage 1 — Query Ingestion & Tokenization

```
User Query ──▶ Lowercase ──▶ Remove Punctuation ──▶ Stopword Filter ──▶ Token List
                                                        │
                                                   73 common English
                                                   stopwords removed
```

The raw query string is normalized: lowercased, non-alphanumeric characters stripped, and filtered through a curated stopword set. The resulting token list feeds both the BM25 and dense retrieval stages.

### Stage 2 — Parallel Hybrid Retrieval

Two retrieval methods execute in parallel on the **same query**:

| Method | Model | What It Does | Top-K |
|--------|-------|-------------|-------|
| **BM25 (Lexical)** | `rank_bm25.BM25Okapi` | Term-frequency scoring against tokenized corpus | 15 |
| **Dense (Semantic)** | `all-MiniLM-L6-v2` (SentenceTransformer) | Cosine similarity between query embedding and pre-computed document embeddings | 15 |

**Score Fusion:**
```
hybrid_score = 0.4 × norm(BM25) + 0.6 × norm(Dense)
```

Min-max normalization brings both score distributions to `[0, 1]` before weighted combination. The top-15 from each method are merged and sorted by hybrid score, yielding up to **15 unique candidates**.

### Stage 3 — Cross-Encoder Re-Ranking

```
15 candidates ──▶ Cross-Encoder (ms-marco-TinyBERT-L-2-v2) ──▶ Top 5 final results
                      │
                  Pairwise (query, document) scoring
                  Much more accurate than bi-encoder
```

The cross-encoder processes **(query, document_text)** pairs, producing a fine-grained relevance score. This is the most expensive step but dramatically improves precision. The final **top-5** standards are returned.

### Stage 4 — Rationale Generation (Optional)

For single-query mode (not batch evaluation), the engine calls **Claude 3.5 Haiku** via the Anthropic API to generate a 2-3 sentence expert rationale explaining why the retrieved standards match the query. This step is **skipped during batch evaluation** for latency optimization.

### Pipeline Summary

```
                    ┌─────────────────────────────┐
                    │        User Query            │
                    └──────────┬──────────────────-┘
                               │
                    ┌──────────▼──────────────────-┐
                    │      Tokenize & Normalize     │
                    └──────────┬──────────────────-─┘
                               │
                ┌──────────────┼──────────────────┐
                │              │                  │
        ┌───────▼───────┐  ┌──▼──────────────┐   │
        │   BM25 Search │  │  Dense Search   │   │
        │   (Top 15)    │  │  (Top 15)       │   │
        └───────┬───────┘  └──┬──────────────┘   │
                │              │                  │
                └──────┬───────┘                  │
                       │                          │
              ┌────────▼─────────┐                │
              │  Hybrid Score    │                 │
              │  Fusion & Merge  │                 │
              │  (Up to 15)      │                 │
              └────────┬─────────┘                 │
                       │                           │
              ┌────────▼─────────┐                 │
              │  Cross-Encoder   │                 │
              │  Re-Ranking      │                 │
              │  (Top 5)         │                 │
              └────────┬─────────┘                 │
                       │                           │
              ┌────────▼─────────┐                 │
              │  Claude Haiku    │ ◀── Optional     │
              │  Rationale       │    (single query │
              └────────┬─────────┘     mode only)   │
                       │                           │
              ┌────────▼─────────┐                 │
              │  Final Response  │                 │
              │  {standards,     │                 │
              │   rationale,     │                 │
              │   latency}       │                 │
              └──────────────────┘
```

---

## 📊 Document Representation

Each standard in `standards_enriched.json` is indexed as a **unified text block** composed of:

```
standardNumber + title + description + section + keywords + contextChunks
```

This unified text is used for:
- **BM25 tokenized corpus** (bag-of-words index)
- **Dense embeddings** (single 384-dim vector via MiniLM)
- **Cross-encoder input** (paired with query for pairwise scoring)

---

## 🚀 Features

- **Three-Stage Hybrid Retrieval**: BM25 lexical + dense semantic + cross-encoder re-ranking
- **Zero Hard-Coded Facts**: All knowledge comes from the external standards JSON — no keyword aliases
- **Expert Rationale**: Uses Claude 3.5 Haiku to explain why specific standards are relevant
- **Real-Time Evaluation**: Frontend "Run Evaluation" button triggers fresh retrieval against the test set
- **Low Latency**: Optimized candidate pool sizes for <3s average per query
- **PDF Ingestion**: Upload BIS standard PDFs to auto-extract and add to the corpus
- **Premium UI**: GSAP animations, tracking cursor, dark glassmorphism design

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10+, FastAPI, Uvicorn |
| **Retrieval** | `rank-bm25`, `sentence-transformers` (MiniLM), Cross-Encoder (TinyBERT) |
| **AI** | Anthropic Claude 3.5 Haiku (rationale generation) |
| **Frontend** | React 19, TypeScript, Vite, GSAP, Tailwind CSS |
| **Data** | JSON standards corpus, PDFPlumber for extraction |

---

## 📦 Project Structure

```
BIS RAG/
├── backend/
│   ├── api.py                  # FastAPI server (query, evaluate endpoints)
│   ├── inference.py            # Core BISRetrievalEngine (BM25 + Dense + CrossEncoder)
│   ├── eval_script.py          # Evaluation runner script
│   ├── enrich_standards.py     # One-time enrichment script for standards.json
│   ├── pdf_extractor.py        # Extract standards from BIS PDF documents
│   ├── generate_mappings.py    # Generate direct mapping suggestions
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # Main app layout
│   │   ├── main.tsx            # React entry point
│   │   ├── index.css           # Global styles
│   │   ├── components/         # UI components
│   │   │   ├── SearchDemo.tsx          # Live query interface
│   │   │   ├── EvaluationDashboard.tsx # Real-time benchmarking panel
│   │   │   ├── Pipeline.tsx            # Pipeline visualization
│   │   │   ├── Architecture.tsx        # Architecture diagram
│   │   │   ├── Metrics.tsx             # Performance metrics display
│   │   │   ├── Hero.tsx                # Landing hero section
│   │   │   ├── Navbar.tsx              # Navigation bar
│   │   │   ├── CTAFooter.tsx           # Call-to-action footer
│   │   │   └── ...                     # Other UI components
│   │   ├── config/
│   │   │   └── api.ts          # API client configuration
│   │   ├── data/
│   │   │   └── standards.ts    # Standards data
│   │   └── utils/
│   │       └── cn.ts           # Class name utilities
│   ├── public/
│   │   ├── standards_enriched.json  # Enriched standards corpus (568 standards)
│   │   └── standards.json           # Raw standards corpus
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── index.html
├── data/
│   ├── standards.json          # Raw standards corpus
│   ├── standards_enriched.json # Enriched corpus (with descriptions, keywords, chunks)
│   ├── public_test_set.json    # Evaluation test set (queries + expected standards)
│   ├── public_test_set1.json   # Alternative test set
│   ├── queries_200.json        # Additional queries
│   ├── team_results.json       # Latest evaluation results
│   ├── private_data_set.json   # Private dataset
│   └── dataset.pdf             # BIS PDF document
├── .env                        # Environment variables (API keys)
├── .gitignore                  # Git ignore rules
├── render.yaml                 # Render.com deployment blueprint
├── vercel.json                 # Vercel deployment config
├── DEPLOY.md                   # Deployment instructions
├── VERCEL_DEPLOY.md            # Vercel-specific deployment guide
├── inference.py                # Root wrapper (forwards to backend/inference.py)
├── eval_script.py              # Standalone evaluation runner wrapper
└── README.md
```

---

## ⚡ Setup & Installation

### Prerequisites
- **Python**: 3.10 or higher
- **Node.js**: 18 or higher
- **npm**: 9 or higher
- **Anthropic API Key**: Optional (for rationale generation using Claude 3.5 Haiku)

### Step 1: Clone & Navigate to Project

```bash
git clone https://github.com/dharmik2587/bishackathon.git
cd bishackathon
```

### Step 2: Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Dependencies installed:**
- `rank-bm25==0.2.2` — BM25 lexical search
- `nltk==3.9.1` — Natural language processing
- `numpy>=1.24.0` — Numerical computing
- `sentence-transformers>=2.2.0` — Dense embeddings (all-MiniLM-L6-v2) and cross-encoder re-ranking
- `requests>=2.28.0` — HTTP client for Anthropic API calls
- `thefuzz==0.22.1` — Fuzzy string matching / typo tolerance
- `python-Levenshtein==0.26.1` — Fast Levenshtein distance computation
- `fastapi==0.104.1` — Web framework
- `uvicorn[standard]==0.24.0` — ASGI server
- `pydantic==2.5.0` — Data validation
- `python-dotenv==1.1.0` — Environment variables

#### Setup Environment Variables

Create or verify `.env` file in the **project root** (`BIS RAG/`):

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

**Note:** The ANTHROPIC_API_KEY is optional. If not provided, the engine will still work but won't generate explanatory rationales for query results.

### Step 3: Frontend Setup

```bash
cd frontend
npm install
```

This installs all React, TypeScript, Vite, Tailwind CSS, and animation dependencies.

---

## 🚀 Running the Application

### Option A: Run Backend Only (API Server)

Best for testing the backend API independently or for deployment.

```bash
cd backend
python api.py
```

**Expected Output:**
```
[OK] BIS RAG Engine loaded with 568 standards
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The API will:
1. Load 568 standards from `frontend/public/standards_enriched.json` (or fallback to `data/standards.json`)
2. Build BM25 index and encode document embeddings (~15-30 seconds)
3. Load cross-encoder model for re-ranking
4. Serve on **http://localhost:8000**

**Test the API (PowerShell):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/" -Method GET
```

**Test the API (bash/curl):**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "galvanized iron pipes", "top_k": 5}'
```

### Option B: Run Frontend Only (Development Server)

Best for frontend UI development and testing.

```bash
cd frontend
npm install
npm run dev
```

**Expected Output:**
```
VITE v7.3.2 ready in XXX ms

  ➜  Local:   http://localhost:5173/
```

Open **http://localhost:5173** in your browser. The frontend will proxy API requests to `http://localhost:8000`.

**Note:** Make sure the backend is running before using the frontend's search and evaluation features.

### Option C: Run Full Stack (Recommended for Testing)

Run both backend and frontend in separate terminals:

**Terminal 1 — Backend:**
```bash
cd backend
python api.py
# Wait for "[OK] BIS RAG Engine loaded with 568 standards"
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
# Visit http://localhost:5173
```

Now you can:
- Use the **Search Demo** component to query the engine
- Click **Run Evaluation** to benchmark against the test set
- View real-time results in the **Evaluation Dashboard**
- Explore the **Pipeline Visualization** and **Architecture** diagrams

---

## 📊 API Endpoints

All endpoints expect and return JSON. The backend runs on `http://localhost:8000`.

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| `GET` | `/` | Health check | `curl http://localhost:8000/` |
| `POST` | `/api/query` | Query the engine | See below |
| `POST` | `/api/evaluate` | Run full evaluation | `curl -X POST http://localhost:8000/api/evaluate` |
| `GET` | `/api/results` | Get latest evaluation results | `curl http://localhost:8000/api/results` |
| `GET` | `/api/standards` | List indexed standards (paginated) | `curl "http://localhost:8000/api/standards?limit=10&offset=0"` |
| `GET` | `/api/standards/{standard_number}` | Get single standard details | `curl http://localhost:8000/api/standards/BIS-1234` |

### Query Endpoint (`POST /api/query`)

**Request:**
```json
{
  "query": "Which standard applies to galvanized iron pipes?",
  "top_k": 5
}
```

**Response:**
```json
{
  "id": "q-1705000000000",
  "query": "Which standard applies to galvanized iron pipes?",
  "retrieved_standards": [
    {
      "id": "std-001",
      "standardNumber": "BIS 6745",
      "title": "Zinc coated (galvanized) steel tubes",
      "category": "Materials",
      "description": "Specification for zinc coated...",
      "keywords": ["galvanized", "zinc", "steel tubes"],
      "contextChunks": ["..."]
    }
  ],
  "rationale": "These standards cover galvanized steel products and coatings.",
  "latency_seconds": 0.523,
  "timestamp": 1705000000000
}
```

### Evaluate Endpoint (`POST /api/evaluate`)

Runs the engine against the full public test set and returns aggregate metrics.

**Response:**
```json
{
  "total_queries": 20,
  "hit_rate_3": 85.0,
  "mrr_5": 0.78,
  "avg_latency": 0.45,
  "results": [
    {
      "id": "q-001",
      "query": "...",
      "expected_standards": ["BIS-1234", "BIS-5678"],
      "retrieved_standards": ["BIS-1234", "BIS-9999", "BIS-5678"],
      "latency_seconds": 0.35
    }
  ]
}
```

---

## 📈 Running Evaluations

### Via Frontend UI (Recommended)

1. Start both backend and frontend (see "Run Full Stack" above)
2. Navigate to **http://localhost:5173**
3. Scroll to **Evaluation Dashboard**
4. Click **"Run Evaluation"** button
5. Results appear in real-time with metrics

### Via Command Line

From the **project root**:

```bash
python inference.py --input data/public_test_set.json --output team_results.json
```

Or from the **backend** directory:

```bash
cd backend
python inference.py --input ../data/public_test_set.json --output ../team_results.json
```

**Expected Output:**
```
Processed 20 queries...
Hit Rate @3: 85.0%
MRR @5: 0.78
Average Latency: 0.45s
Results saved to team_results.json
```

### Evaluation Metrics

| Metric | Description | Formula |
|--------|-------------|---------|
| **Hit Rate @3** | % of queries where >=1 expected standard appears in top-3 results | `(# hits / total) x 100` |
| **MRR @5** | Mean reciprocal rank of first correct standard in top-5 | `mean(1 / rank)` for rank in [1,5] |
| **Avg Latency** | Average query processing time in seconds | `total_time / num_queries` |

---

## 🛠️ Development & Troubleshooting

### Issue: Port 8000 Already in Use

**Solution:**
```powershell
# On Windows (PowerShell):
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

```bash
# On macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

Then restart the backend.

### Issue: Module Not Found (`from .inference import...`)

**Solution:**
The codebase now uses absolute imports. Ensure you're running:
```bash
cd backend
python api.py
```

Do NOT run `python -m uvicorn backend.api:app` from the project root.

### Issue: Standards File Not Found

**Solution:**
Verify `frontend/public/standards_enriched.json` exists. If not, copy from data:
```bash
cp data/standards_enriched.json frontend/public/standards_enriched.json
```

### Issue: Frontend Proxy Not Working

**Solution:**
Ensure the backend is running on port 8000. Check `frontend/vite.config.ts`:
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```

### Clearing Cache

```powershell
# Python cache
Remove-Item -Recurse -Force backend\__pycache__ -ErrorAction SilentlyContinue

# Node modules (frontend)
Remove-Item -Recurse -Force frontend\node_modules -ErrorAction SilentlyContinue
cd frontend; npm install; cd ..
```

---

## ☁️ Deployment

This repository includes a `render.yaml` for one-click deployment on Render.com:
1. Connect your GitHub repository to Render
2. Render auto-detects the blueprint and deploys both services
3. Add `ANTHROPIC_API_KEY` in Render environment variables

---

**Made with ❤️ by Dharmik (Backend) & Aayasha Patel (Frontend)**
