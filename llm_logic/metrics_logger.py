"""
metrics_logger.py — Token & Quality Metrics Logger
Teammate 2: LLM Integration & Modernization Suggester
"""

import json
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional
from modernizer import ModernizationResult


METRICS_FILE = Path("metrics_log.jsonl")  # One JSON object per line


@dataclass
class RunMetrics:
    # Identification
    run_id: str
    timestamp: str

    # Input metadata
    source_language: str
    target_language: str
    source_file: Optional[str]

    # Token counts
    raw_tokens: int            # Tokens BEFORE context optimization (from Teammate 1)
    optimized_tokens: int      # Tokens AFTER optimization (what we actually sent)
    completion_tokens: int     # Tokens in the LLM's response
    total_tokens_used: int

    # Reduction stats
    token_reduction_abs: int   # raw - optimized
    token_reduction_pct: float # % reduced

    # Quality signals
    hallucination_flag_count: int
    warning_count: int
    llm_latency_ms: float
    success: bool

    # Derived quality score (0–100)
    quality_score: float = 0.0
    error: Optional[str] = None
    notes: list[str] = field(default_factory=list)


class MetricsLogger:
    def __init__(self, log_file: Path = METRICS_FILE):
        self.log_file = log_file

    def log(
        self,
        result: ModernizationResult,
        raw_token_count: int,           # Before Teammate 1 optimization
        source_file: Optional[str] = None,
    ) -> RunMetrics:
        """
        Compute and persist all metrics for one modernization run.
        raw_token_count comes from Teammate 1's context_optimizer output.
        """
        llm = result.llm_response

        optimized_tokens = llm.prompt_tokens if llm else 0
        completion_tokens = llm.completion_tokens if llm else 0
        total_tokens = llm.total_tokens if llm else 0
        latency_ms = llm.latency_ms if llm else 0.0

        reduction_abs = max(raw_token_count - optimized_tokens, 0)
        reduction_pct = (reduction_abs / raw_token_count * 100) if raw_token_count > 0 else 0.0

        quality_score = self._compute_quality_score(
            result=result,
            reduction_pct=reduction_pct,
        )

        metrics = RunMetrics(
            run_id=f"run_{int(time.time() * 1000)}",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            source_language=result.source_language,
            target_language=result.target_language,
            source_file=source_file,
            raw_tokens=raw_token_count,
            optimized_tokens=optimized_tokens,
            completion_tokens=completion_tokens,
            total_tokens_used=total_tokens,
            token_reduction_abs=reduction_abs,
            token_reduction_pct=round(reduction_pct, 2),
            hallucination_flag_count=len(result.hallucination_flags),
            warning_count=len(result.warnings),
            llm_latency_ms=round(latency_ms, 2),
            success=result.success,
            quality_score=round(quality_score, 1),
            error=result.error,
            notes=result.hallucination_flags + result.warnings,
        )

        self._write(metrics)
        return metrics

    def summary(self) -> dict:
        """
        Read all logged runs and return aggregate stats.
        Used by the /metrics/summary FastAPI endpoint.
        """
        runs = self._read_all()
        if not runs:
            return {"total_runs": 0}

        successful = [r for r in runs if r["success"]]
        reductions = [r["token_reduction_pct"] for r in successful]
        quality_scores = [r["quality_score"] for r in successful]
        latencies = [r["llm_latency_ms"] for r in successful]

        return {
            "total_runs": len(runs),
            "successful_runs": len(successful),
            "failed_runs": len(runs) - len(successful),
            "avg_token_reduction_pct": round(sum(reductions) / len(reductions), 2) if reductions else 0,
            "max_token_reduction_pct": round(max(reductions), 2) if reductions else 0,
            "avg_quality_score": round(sum(quality_scores) / len(quality_scores), 1) if quality_scores else 0,
            "avg_latency_ms": round(sum(latencies) / len(latencies), 1) if latencies else 0,
            "total_tokens_saved": sum(r["token_reduction_abs"] for r in successful),
            "runs": runs[-10:],  # Last 10 runs for display
        }

    # ── Private ───────────────────────────────────────────────────────────────

    def _compute_quality_score(
        self,
        result: ModernizationResult,
        reduction_pct: float,
    ) -> float:
        """
        Score 0–100 based on:
        - 40pts: success (binary)
        - 30pts: no hallucination flags
        - 20pts: token reduction achieved
        - 10pts: no warnings
        """
        if not result.success:
            return 0.0

        score = 40.0

        # Hallucination penalty: -10 per flag, min 0
        flag_penalty = min(len(result.hallucination_flags) * 10, 30)
        score += 30 - flag_penalty

        # Token reduction reward: up to 20pts for ≥50% reduction
        reduction_score = min(reduction_pct / 50 * 20, 20)
        score += reduction_score

        # Warning penalty: -5 per warning
        warning_penalty = min(len(result.warnings) * 5, 10)
        score += 10 - warning_penalty

        return score

    def _write(self, metrics: RunMetrics):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(metrics)) + "\n")

    def _read_all(self) -> list[dict]:
        if not self.log_file.exists():
            return []
        runs = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        runs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return runs
