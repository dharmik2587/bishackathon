from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import json
import os
import time
from pathlib import Path
import sys
from pathlib import Path as PathlibPath

# Add backend directory to path for imports
sys.path.insert(0, str(PathlibPath(__file__).parent))

from inference import AccurateFastRetriever

app = FastAPI(title="BIS Standards RAG Engine API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ],  # Frontend dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engine instance
engine: Optional[AccurateFastRetriever] = None

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class StandardInfo(BaseModel):
    id: str
    standardNumber: str
    title: str
    category: str
    description: str
    keywords: List[str]
    contextChunks: List[str]

class QueryResponse(BaseModel):
    id: str
    query: str
    retrieved_standards: List[StandardInfo]
    rationale: Optional[str] = None
    latency_seconds: float
    timestamp: int

class EvaluationResult(BaseModel):
    id: str
    query: str
    expected_standards: Optional[List[str]] = None
    retrieved_standards: List[str]
    rationale: Optional[str] = None
    latency_seconds: float

class EvaluationMetrics(BaseModel):
    total_queries: int
    hit_rate_3: float
    mrr_5: float
    avg_latency: float
    results: Optional[List[EvaluationResult]] = None

@app.on_event("startup")
async def startup_event():
    global engine
    # Load standards from the enriched JSON
    standards_path = Path(__file__).parent.parent / "frontend" / "public" / "standards_enriched.json"
    if not standards_path.exists():
        # Fallback to data directory
        standards_path = Path(__file__).parent.parent / "data" / "standards.json"

    if not standards_path.exists():
        raise RuntimeError(f"Standards file not found at {standards_path}")

    try:
        engine = AccurateFastRetriever(str(standards_path))
        print(f"[OK] BIS RAG Engine loaded with {len(engine.standards)} standards")
    except Exception as e:
        print(f"[ERROR] Failed to load engine: {e}")
        raise


def normalize_std(std_string: str) -> str:
    return str(std_string).replace(" ", "").lower()


def compute_evaluation_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_queries = len(results)
    if total_queries == 0:
        return {
            "total_queries": 0,
            "hit_rate_3": 0.0,
            "mrr_5": 0.0,
            "avg_latency": 0.0,
        }

    hits_at_3 = 0
    mrr_sum = 0.0
    total_latency = 0.0

    for item in results:
        expected = {normalize_std(std) for std in item.get("expected_standards", [])}
        retrieved = [normalize_std(std) for std in item.get("retrieved_standards", [])]
        total_latency += item.get("latency_seconds", 0.0)

        if expected and any(std in expected for std in retrieved[:3]):
            hits_at_3 += 1

        mrr = 0.0
        for rank, std in enumerate(retrieved[:5], start=1):
            if std in expected:
                mrr = 1.0 / rank
                break
        mrr_sum += mrr

    return {
        "total_queries": total_queries,
        "hit_rate_3": round((hits_at_3 / total_queries) * 100, 2),
        "mrr_5": round(mrr_sum / total_queries, 4),
        "avg_latency": round(total_latency / total_queries, 4),
    }


def load_results_file() -> List[Dict[str, Any]]:
    root = Path(__file__).parent.parent
    candidates = [
        root / "team_results.json",
        root / "data" / "team_results.json",
    ]
    for path in candidates:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    return []


def load_public_test_set() -> List[Dict[str, Any]]:
    root = Path(__file__).parent.parent
    candidates = [
        root / "data" / "public_test_set.json",
        root / "data" / "public_test_set1.json",
    ]
    for path in candidates:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    return []


@app.get("/")
async def root():
    return {"message": "BIS Standards RAG Engine API", "status": "running"}

@app.post("/api/query", response_model=QueryResponse)
async def query_standards(request: QueryRequest):
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    try:
        import time
        start_time = time.time()

        retrieved_numbers = engine.retrieve(request.query, top_k=request.top_k)

        retrieved_standards = []
        for std_num in retrieved_numbers:
            std_data = next(
                (std for std in engine.standards if std.get("standardNumber") == std_num),
                None
            )
            if std_data:
                retrieved_standards.append(StandardInfo(**std_data))

        latency = time.time() - start_time

        rationale = "Matched via hybrid BM25 lexical + dense semantic retrieval with cross-encoder re-ranking."

        return QueryResponse(
            id=f"q-{int(start_time * 1000)}",
            query=request.query,
            retrieved_standards=retrieved_standards,
            rationale=rationale,
            latency_seconds=round(latency, 3),
            timestamp=int(start_time * 1000)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/api/results", response_model=EvaluationMetrics)
async def get_results():
    results = load_results_file()
    metrics = compute_evaluation_metrics(results)
    return EvaluationMetrics(**metrics, results=results)


@app.post("/api/evaluate", response_model=EvaluationMetrics)
async def run_evaluation():
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    queries = load_public_test_set()
    if not queries:
        raise HTTPException(status_code=500, detail="Public test set not found")

    results: List[Dict[str, Any]] = []
    total_time = 0.0

    for q in queries:
        if not isinstance(q, dict) or "id" not in q or "query" not in q:
            continue

        start_time = time.time()
        retrieved_numbers = engine.retrieve(q["query"], top_k=5)
        latency = round(time.time() - start_time, 4)
        total_time += latency

        result = {
            "id": q["id"],
            "query": q["query"],
            "retrieved_standards": retrieved_numbers,
            "rationale": "Matched via hybrid retrieval with cross-encoder re-ranking.",
            "latency_seconds": latency,
        }
        if "expected_standards" in q:
            result["expected_standards"] = q["expected_standards"]
        results.append(result)

    metrics = compute_evaluation_metrics(results)
    return EvaluationMetrics(**metrics, results=results)


@app.get("/api/standards/{standard_number}", response_model=StandardInfo)
async def get_standard(standard_number: str):
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    # Find the standard
    for std in engine.standards:
        if std["standardNumber"] == standard_number:
            return StandardInfo(**std)

    raise HTTPException(status_code=404, detail="Standard not found")

@app.get("/api/standards", response_model=List[StandardInfo])
async def list_standards(limit: Optional[int] = 100, offset: Optional[int] = 0):
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    standards = engine.standards[offset:offset + limit] if limit else engine.standards[offset:]
    return [StandardInfo(**std) for std in standards]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)