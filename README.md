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
│  │  rank_bm25       all-MiniLM         ms-marco-MiniLM       │  │
│  │  (Okapi)         L6-v2              L-6-v2                │  │
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
15 candidates ──▶ Cross-Encoder (ms-marco-MiniLM-L-6-v2) ──▶ Top 5 final results
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
| **Retrieval** | `rank-bm25`, `sentence-transformers` (MiniLM), Cross-Encoder |
| **AI** | Anthropic Claude 3.5 Haiku (rationale generation) |
| **Frontend** | React 19, TypeScript, Vite, GSAP, Tailwind CSS |
| **Data** | JSON standards corpus, PDFPlumber for extraction |

---

## 📦 Project Structure

```
BIS RAG/
├── backend/
│   ├── api.py                  # FastAPI server (query, evaluate, upload endpoints)
│   ├── inference.py            # Core BISRetrievalEngine (BM25 + Dense + CrossEncoder)
│   ├── enrich_standards.py     # One-time enrichment script for standards.json
│   ├── pdf_extractor.py        # Extract standards from BIS PDF documents
│   └── generate_mappings.py    # Generate direct mapping suggestions
├── data/
│   ├── standards.json          # Raw standards corpus (570+ entries)
│   ├── standards_enriched.json # Enriched corpus (with descriptions, keywords, chunks)
│   ├── public_test_set.json    # Public evaluation test set (20 queries)
│   └── team_results.json       # Latest evaluation results
├── FRONTEND-UP/
│   ├── src/
│   │   ├── App.tsx             # Main app layout
│   │   ├── components/
│   │   │   ├── SearchDemo.tsx          # Live query interface
│   │   │   ├── EvaluationDashboard.tsx # Real-time benchmarking panel
│   │   │   ├── Pipeline.tsx            # Pipeline visualization
│   │   │   ├── Architecture.tsx        # Architecture diagram
│   │   │   ├── Metrics.tsx             # Performance metrics display
│   │   │   ├── Hero.tsx                # Landing hero section
│   │   │   └── ...                     # Navbar, Footer, etc.
│   │   └── index.css           # Global styles
│   └── package.json
├── inference.py                # Root wrapper (forwards to backend/inference.py)
├── eval_script.py              # Standalone evaluation runner
├── .env                        # API keys (ANTHROPIC_API_KEY)
├── render.yaml                 # Render.com deployment blueprint
└── README.md
```

---

## ⚡ Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Anthropic API Key (optional, for rationale generation)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the **project root**:
```env
ANTHROPIC_API_KEY=your_key_here
```

Start the API server:
```bash
python api.py
```

The engine will:
1. Load `data/standards_enriched.json` (falls back to `data/standards.json`)
2. Build BM25 index and encode 570+ document embeddings
3. Load cross-encoder model for re-ranking
4. Run initial evaluation against the public test set
5. Serve API on `http://localhost:8000`

### Frontend Setup

```bash
cd FRONTEND-UP
npm install
npm run dev
```

The frontend serves on `http://localhost:5173` and connects to the backend at `http://localhost:8000`.

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|------------|
| `GET` | `/` | Health check |
| `POST` | `/api/query` | Query the engine with natural language |
| `POST` | `/api/evaluate` | Run fresh evaluation against public test set |
| `GET` | `/api/results` | Get latest saved evaluation results |
| `POST` | `/api/upload_pdf` | Upload and ingest a BIS PDF |
| `GET` | `/api/standards` | List indexed standards (paginated) |

### Query Example
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Which standard applies to galvanized iron pipes?", "top_k": 5}'
```

---

## 📈 Evaluation

Run from the project root:
```bash
python inference.py --input public_test_set.json --output team_results.json
```

Or trigger via the frontend **"Run Evaluation"** button, which calls `POST /api/evaluate` and runs the full pipeline in real-time against every query in the test set.

### Evaluation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Hit Rate @3** | % of queries where correct standard appears in top 3 | >80% |
| **MRR @5** | Mean Reciprocal Rank across top 5 results | >0.70 |
| **Avg Latency** | Average time per query (seconds) | <5.0s |

Queries with **empty `expected_standards`** are excluded from accuracy metrics but included in latency calculations.

---

## ☁️ Deployment

This repository includes a `render.yaml` for one-click deployment on Render.com:
1. Connect your GitHub repository to Render
2. Render auto-detects the blueprint and deploys both services
3. Add `ANTHROPIC_API_KEY` in Render environment variables

---

**Made with ❤️ by Dharmik (Backend) & Aayasha Patel (Frontend)**
