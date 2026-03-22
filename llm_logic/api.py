"""
api.py — FastAPI Backend
Teammate 2: REST endpoints consumed by the React frontend
"""

import sys

# Windows consoles often default to cp1252; printing API/LLM text with Unicode then raises UnicodeEncodeError.
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import os
import requests as http_requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from openrouter_client import OpenRouterClient
from modernizer import CodeModernizer
from metrics_logger import MetricsLogger

# Load environment variables
load_dotenv()

# ── Import Teammate 1's ScaleDown compressor ─────────────────────────────────
# Looks for scaledown.py in legacy-modernizer/legacy-modernizer/
TEAMMATE1_PATH = os.path.join(os.path.dirname(__file__), "..", "legacy-modernizer", "legacy-modernizer")
sys.path.insert(0, os.path.abspath(TEAMMATE1_PATH))

try:
    from scaledown import compress_code
    SCALEDOWN_AVAILABLE = True
    print("[SUCCESS] Teammate 1 ScaleDown connected")
except ImportError as e:
    SCALEDOWN_AVAILABLE = False
    print(f"[WARNING] ScaleDown not found ({e}) - running without compression")
    def compress_code(code): return code  # fallback no-op


# ── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Legacy Code Modernization Engine",
    description="Converts COBOL/Java to Python/Go using LLM with context optimization",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
        "http://localhost:5000",   # Teammate 3's Flask
        "http://127.0.0.1:5000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singletons
logger = MetricsLogger()


DEFAULT_API_KEY = ""  # Set HF_API_KEY environment variable or paste your HF token here

def get_modernizer() -> CodeModernizer:
    api_key = os.environ.get("HF_API_KEY", DEFAULT_API_KEY)
    return CodeModernizer(client=OpenRouterClient(api_key=api_key))


# ── Request / Response Models ────────────────────────────────────────────────

class ModernizeRequest(BaseModel):
    code: str = Field(..., description="The legacy source code to modernize")
    source_language: Optional[str] = Field(None, description="'cobol' or 'java'")
    target_language: str = Field(default="python", description="'python' or 'go'")
    # raw_token_count comes from Teammate 1's context_optimizer.
    # If not provided, we estimate from the raw code directly.
    raw_token_count: Optional[int] = Field(
        default=None,
        description="Token count BEFORE optimization (from Teammate 1). Used for reduction metrics.",
    )
    source_file: Optional[str] = Field(default=None, description="Filename for logging purposes")


class ModernizeResponse(BaseModel):
    success: bool
    source_language: str
    target_language: str
    modernized_code: str
    output: Optional[str] = None
    hallucination_flags: list[str]
    warnings: list[str]
    metrics: dict
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    api_key_set: bool
    model: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Check service health and API key status."""
    api_key = os.environ.get("HF_API_KEY", DEFAULT_API_KEY)
    return HealthResponse(
        status="ok",
        api_key_set=bool(api_key),
        model=os.environ.get("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3"),
    )


@app.post("/modernize")
def modernize_code(request: ModernizeRequest):
    """
    Main endpoint — takes legacy code + metadata, returns modernized code.
    Called by the React frontend after Teammate 1 has run context optimization.
    """
    try:
        if not request.code.strip():
            raise HTTPException(status_code=400, detail="Code cannot be empty")

        lang = request.source_language
        if not lang:
            lower_c = request.code.lower()
            if "identification division" in lower_c or "procedure division" in lower_c:
                lang = "cobol"
            else:
                lang = "java"

        if request.target_language.lower() not in ("python", "go"):
            raise HTTPException(status_code=400, detail="target_language must be 'python' or 'go'")

        # ── Step 1: Compress via Teammate 1's ScaleDown ───────────────────────────
        raw_tokens = request.raw_token_count or max(1, len(request.code) // 4)
        compressed_code = compress_code(request.code)
        optimized_tokens = max(1, len(compressed_code) // 4)
        print(f"[SCALEDOWN] {raw_tokens} -> {optimized_tokens} tokens ({100 - int(optimized_tokens/raw_tokens*100)}% reduction)")

        # ── Step 2: Send compressed code to LLM ──────────────────────────────────
        modernizer = get_modernizer()
        result = modernizer.modernize(
            code=compressed_code,
            source_language=lang,
            target_language=request.target_language,
        )

        metrics = logger.log(
            result=result,
            raw_token_count=raw_tokens,
            source_file=request.source_file,
        )

        return ModernizeResponse(
            success=result.success,
            source_language=lang,
            target_language=result.target_language,
            modernized_code=result.modernized_code,
            output=result.modernized_code,
            hallucination_flags=result.hallucination_flags,
            warnings=result.warnings,
            metrics={
                "run_id": metrics.run_id,
                "raw_tokens": metrics.raw_tokens,
                "optimized_tokens": metrics.optimized_tokens,
                "token_reduction_pct": metrics.token_reduction_pct,
                "token_reduction_abs": metrics.token_reduction_abs,
                "quality_score": metrics.quality_score,
                "llm_latency_ms": metrics.llm_latency_ms,
            },
            error=result.error,
        )
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail={"error_trace": traceback.format_exc(), "error_msg": str(e)})


@app.post("/modernize/github")
def modernize_from_github(payload: dict):
    """
    Accepts a GitHub repo URL, fetches all Java/COBOL files,
    and modernizes each one.
    """
    import re
    github_url = payload.get("github_url", "").strip()
    target_language = payload.get("target_language", "python")

    if not github_url:
        raise HTTPException(status_code=400, detail="github_url is required")

    # Convert GitHub URL to API URL
    # https://github.com/USER/REPO -> https://api.github.com/repos/USER/REPO/contents
    match = re.match(r"https://github\.com/([^/]+)/([^/]+?)(?:\.git)?$", github_url)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL format")

    owner, repo = match.group(1), match.group(2)
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    try:
        response = http_requests.get(api_url, timeout=10)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Could not fetch repo: {response.text}")

        files = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub API error: {str(e)}")

    results = []
    for file in files:
        filename = file.get("name", "")
        if not (filename.endswith(".java") or filename.endswith(".cbl") or filename.endswith(".cob")):
            continue

        source_language = "cobol" if filename.endswith((".cbl", ".cob")) else "java"

        # Fetch raw file content
        raw_url = file.get("download_url")
        if not raw_url:
            continue

        code_response = http_requests.get(raw_url, timeout=10)
        if code_response.status_code != 200:
            continue

        code = code_response.text
        raw_tokens = max(1, len(code) // 4)
        compressed_code = compress_code(code)

        modernizer = get_modernizer()
        result = modernizer.modernize(
            code=compressed_code,
            source_language=source_language,
            target_language=target_language,
        )

        metrics = logger.log(result=result, raw_token_count=raw_tokens, source_file=filename)

        results.append({
            "file": filename,
            "source_language": source_language,
            "target_language": target_language,
            "success": result.success,
            "modernized_code": result.modernized_code,
            "hallucination_flags": result.hallucination_flags,
            "warnings": result.warnings,
            "metrics": {
                "raw_tokens": metrics.raw_tokens,
                "optimized_tokens": metrics.optimized_tokens,
                "token_reduction_pct": metrics.token_reduction_pct,
                "quality_score": metrics.quality_score,
            },
            "error": result.error,
        })

    if not results:
        raise HTTPException(status_code=404, detail="No Java or COBOL files found in repo root")

    return {"github_url": github_url, "files_processed": len(results), "results": results}


@app.post("/ingest")
def ingest_repo(payload: dict):
    """
    Accepts a GitHub URL or local path, ingests all .java/.cbl files,
    and modernizes each one through the full pipeline.
    """
    from ingest import ingest_and_modernize

    source = payload.get("source", "").strip()
    target_language = payload.get("target_language", "python")
    max_files = payload.get("max_files", 3)

    if not source:
        raise HTTPException(status_code=400, detail="source is required (GitHub URL or local path)")

    result = ingest_and_modernize(
        source=source,
        target_language=target_language,
        api_url="http://127.0.0.1:8000",
        max_files=max_files,
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result


@app.get("/metrics/summary")
def get_metrics_summary():
    """
    Returns aggregate stats across all runs.
    Shown in the React dashboard's metrics panel.
    """
    return logger.summary()


@app.get("/supported-languages")
def get_supported_languages():
    """Returns the supported language pairs for the frontend dropdowns."""
    return {
        "source_languages": ["cobol", "java"],
        "target_languages": ["python", "go"],
        "pairs": [
            {"from": "cobol", "to": "python"},
            {"from": "cobol", "to": "go"},
            {"from": "java", "to": "python"},
            {"from": "java", "to": "go"},
        ],
    }


# ── Dev Runner ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8001, reload=True)