# NoeLegacy — Legacy Code Modernization Engine

> An AI-powered developer tool that ingests legacy COBOL & Java repositories and generates clean, documented Python equivalents — without hallucinating.

---

## What It Does

NoesisForge takes legacy COBOL and Java codebases and converts them into modern Python using a context-optimized LLM pipeline. It strips dead code, builds a dependency graph, compresses the context by ~60%, and runs hallucination checks on every output.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS |
| Backend API | FastAPI, Uvicorn, Pydantic |
| LLM | HuggingFace Inference API, Mistral-7B-Instruct |
| Context Compression | ScaleDown API |
| Dependency Graph | NetworkX |
| Bridge Server | Flask, flask-cors |
| Language | Python 3.10+ |
| Deployment | Vercel (frontend), Railway (backend) |

---

## Folder Structure

```
legacy-code-modernizer/
├── legacy-modernizer/
│   ├── context_optimizer.py
│   ├── dependency_graph.py
│   ├── ingester.py
│   ├── scaledown.py
│   ├── main.py
│   └── .env
├── llm_logic/
│   ├── api.py
│   ├── modernizer.py
│   ├── openrouter_client.py
│   ├── metrics_logger.py
│   ├── ingest.py
│   └── requirements_teammate2.txt
└── legacy-modernizer-ui/
    ├── backend/
    │   └── app.py
    ├── src/
    │   ├── components/
    │   ├── sections/
    │   ├── App.jsx
    │   └── main.jsx
    └── package.json
```

---

## How It Works

```
User pastes code or GitHub URL
        ↓
Ingestion — reads .java / .cbl files
        ↓
Context Optimizer — strips dead code, builds dependency graph
        ↓
ScaleDown API — compresses context by ~60%
        ↓
Mistral-7B (HuggingFace) — generates Python equivalent
        ↓
Hallucination Checks — flags invented identifiers or imports
        ↓
Metrics logged — token reduction %, quality score, latency
        ↓
Clean Python returned to UI
```

---

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- HuggingFace token — https://huggingface.co/settings/tokens
- ScaleDown API key — https://scaledown.xyz

### Install

```bash
# Backend
cd llm_logic
pip install -r requirements_teammate2.txt

# Frontend
cd legacy-modernizer-ui
npm install
```

### Environment Variables

```bash
# llm_logic/openrouter_client.py
HF_API_KEY = "hf_your_token_here"

# legacy-modernizer/.env
SCALEDOWN_API_KEY = "your_key_here"
```

---

## Run Locally

```bash
# Terminal 1 — FastAPI
cd llm_logic
python api.py
# Running at http://127.0.0.1:8001

# Terminal 2 — Flask
cd legacy-modernizer-ui/backend
python app.py
# Running at http://127.0.0.1:5000

# Terminal 3 — React
cd legacy-modernizer-ui
npm run dev
# Running at http://localhost:5173
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Server and API key status |
| POST | `/modernize` | Convert legacy code to Python |
| POST | `/ingest` | Ingest GitHub repo or local path |
| GET | `/metrics/summary` | Token stats and quality scores |
| GET | `/supported-languages` | Available language pairs |

---

## Supported Conversions

| From | To |
|---|---|
| COBOL | Python |
| COBOL | Go |
| Java | Python |
| Java | Go |

---

## Sample Request

```bash
curl -X POST http://127.0.0.1:8001/modernize \
  -H "Content-Type: application/json" \
  -d '{
    "code": "public class Hello { public static void main(String[] args) { System.out.println(\"Hello\"); } }",
    "source_language": "java",
    "target_language": "python"
  }'
```

### Ingest a GitHub Repo

```bash
curl -X POST http://127.0.0.1:8001/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source": "https://github.com/your/repo",
    "target_language": "python",
    "max_files": 3
  }'
```

---

## Context Optimization Results

| Metric | Result |
|---|---|
| Context size reduction | ~60% |
| Dead code passed to LLM | ~0 |
| Quality score range | 0 – 100 |
| Hallucination detection | Identifier + import checks |
