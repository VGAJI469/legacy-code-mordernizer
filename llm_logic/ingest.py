"""
ingest.py — GitHub / Local Repo Ingestion Endpoint
Integrates Teammate 1's CodeIngester with Teammate 2's /modernize pipeline
"""

import os
import sys
import requests
import zipfile
import io


# ── CodeIngester (Teammate 1) ─────────────────────────────────────────────────

class CodeIngester:
    def __init__(self, source):
        self.source = source
        self.files = {}

    def load(self):
        self.files = {}
        if self.source.startswith("http"):
            return self._load_github_repo()
        else:
            return self._load_local_repo()

    def _load_local_repo(self):
        for root, _, files in os.walk(self.source):
            for file in files:
                if file.endswith((".java", ".cbl")):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            self.files[path] = f.read()
                    except:
                        pass
        return self.files

    def _load_github_repo(self):
        branches = ["main", "master"]
        for branch in branches:
            try:
                url = f"{self.source}/archive/refs/heads/{branch}.zip"
                r = requests.get(url, timeout=15)
                if r.status_code != 200:
                    continue
                z = zipfile.ZipFile(io.BytesIO(r.content))
                for file in z.namelist():
                    if file.endswith((".java", ".cbl")):
                        try:
                            self.files[file] = z.read(file).decode("utf-8", errors="ignore")
                        except:
                            pass
                print(f"[OK] Loaded from branch: {branch}")
                return self.files
            except:
                continue
        raise Exception("Failed to load GitHub repo — tried main and master branches")


# ── Ingest + Modernize Pipeline ───────────────────────────────────────────────

def ingest_and_modernize(
    source: str,
    target_language: str = "python",
    api_url: str = "http://127.0.0.1:8000",
    max_files: int = 3,        # Only process first N files
    max_file_size: int = 5000, # Skip files larger than this (chars)
) -> dict:
    """
    Full pipeline:
    1. Ingest repo (GitHub URL or local path)
    2. For each .java / .cbl file found, POST to /modernize
    3. Return all results
    """

    # Step 1 — Ingest
    ingester = CodeIngester(source)
    try:
        files = ingester.load()
    except Exception as e:
        return {"success": False, "error": str(e), "results": []}

    if not files:
        return {"success": False, "error": "No .java or .cbl files found", "results": []}

    # Filter out test files, module-info, and package-info — keep only real source files
    SKIP_PATTERNS = ["test", "Test", "module-info", "package-info", "Main.java"]
    filtered = {
        k: v for k, v in files.items()
        if not any(p in os.path.basename(k) for p in SKIP_PATTERNS)
        and len(v) <= max_file_size
        and len(v) > 50  # skip empty/tiny files
    }

    # Sort by file size ascending — smallest first (cleanest for LLM)
    sorted_files = dict(sorted(filtered.items(), key=lambda x: len(x[1])))

    print(f"[FOUND] Found {len(files)} total — {len(sorted_files)} usable (under {max_file_size} chars) — processing up to {max_files}")

    # Step 2 — Modernize each file (limited)
    results = []
    processed = 0
    for filepath, code in sorted_files.items():
        if processed >= max_files:
            print(f"[SKIP] Skipping remaining files (limit: {max_files})")
            break

        filename = os.path.basename(filepath)
        source_language = "cobol" if filepath.endswith(".cbl") else "java"

        print(f"[PROC] Processing: {filename} ({source_language} -> {target_language})")

        try:
            response = requests.post(
                f"{api_url}/modernize",
                json={
                    "code": code,
                    "source_language": source_language,
                    "target_language": target_language,
                    "source_file": filename,
                    "raw_token_count": max(1, len(code) // 4),
                },
                timeout=120,
            )

            if response.status_code == 200:
                result = response.json()
                results.append({
                    "file": filename,
                    "source_language": source_language,
                    "target_language": target_language,
                    "success": result.get("success"),
                    "modernized_code": result.get("modernized_code"),
                    "hallucination_flags": result.get("hallucination_flags", []),
                    "warnings": result.get("warnings", []),
                    "metrics": result.get("metrics", {}),
                    "error": result.get("error"),
                })
            else:
                results.append({
                    "file": filename,
                    "success": False,
                    "error": f"API error {response.status_code}: {response.text[:100]}",
                })

        except requests.exceptions.ConnectionError:
            results.append({
                "file": filename,
                "success": False,
                "error": "Cannot connect to FastAPI — make sure api.py is running on port 8000",
            })

        processed += 1

    return {
        "success": True,
        "source": source,
        "total_files_found": len(files),
        "total_files_usable": len(sorted_files),
        "processed": len(results),
        "results": results,
    }


# ── CLI Runner ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    # Default test — replace with any GitHub URL or local path
    source = sys.argv[1] if len(sys.argv) > 1 else "https://github.com/VGAJI469/PalindromeCheckerApp"
    target = sys.argv[2] if len(sys.argv) > 2 else "python"

    print(f"\n[START] Ingesting: {source}")
    print(f"[TARGET] Target language: {target}\n")

    output = ingest_and_modernize(source=source, target_language=target)

    for r in output.get("results", []):
        print(f"\n{'='*60}")
        print(f"[FILE] File: {r['file']}")
        print(f"[OK] Success: {r['success']}")
        if r.get("modernized_code"):
            print(f"\n--- Modernized Code ---\n{r['modernized_code']}")
        if r.get("hallucination_flags"):
            print(f"\n[WARN] Flags: {r['hallucination_flags']}")
        if r.get("error"):
            print(f"\n[ERROR] Error: {r['error']}")

    print(f"\n{'='*60}")
    print(f"Total files processed: {output['processed']}/{output['total_files']}")