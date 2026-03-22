"""
modernizer.py — Prompt Engineering & Hallucination Reduction Layer
Teammate 2: LLM Integration & Modernization Suggester
"""

import re
from dataclasses import dataclass, field
from typing import Optional
from openrouter_client import OpenRouterClient, LLMResponse


# ── Prompt Templates ────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a code converter. Convert legacy COBOL or Java code into clean Python or Go.

STRICT RULES:
1. Output ONLY raw code — no comments, no docstrings, no explanations whatsoever
2. No # comments of any kind
3. No [WARN] REVIEW notes
4. No inline explanations
5. Preserve the exact same logic and behavior
6. Use proper naming conventions for the target language
7. Output ONLY the code block, nothing else

Output format:
```<language>
<code only, zero comments>
```
"""

COBOL_TO_PYTHON_PROMPT = """Convert the following COBOL code to Python 3.10+.
- Map COBOL divisions (DATA, PROCEDURE) to Python classes/functions
- Replace PERFORM loops with for/while loops
- Replace MOVE statements with variable assignments
- Use snake_case for all identifiers

COBOL INPUT:
{code}

Target language: Python
"""

JAVA_TO_PYTHON_PROMPT = """Convert the following Java code to Python 3.10+.
- Replace Java classes with Python dataclasses or plain classes
- Replace static void main with an if __name__ == '__main__' guard
- Use Python type hints mirroring the Java types
- Replace checked exceptions with Python try/except

JAVA INPUT:
{code}

Target language: Python
"""

JAVA_TO_GO_PROMPT = """Convert the following Java code to idiomatic Go.
- Map Java classes to Go structs
- Replace Java interfaces with Go interfaces
- Use Go error return patterns instead of exceptions
- Follow Go naming conventions (CamelCase exported, camelCase unexported)

JAVA INPUT:
{code}

Target language: Go
"""

COBOL_TO_GO_PROMPT = """Convert the following COBOL code to idiomatic Go.
- Map COBOL paragraphs to Go functions
- Use Go structs for COBOL data records
- Replace PERFORM with Go loops
- Use Go error handling patterns

COBOL INPUT:
{code}

Target language: Go
"""

PROMPT_MAP = {
    ("cobol", "python"): COBOL_TO_PYTHON_PROMPT,
    ("java", "python"): JAVA_TO_PYTHON_PROMPT,
    ("java", "go"): JAVA_TO_GO_PROMPT,
    ("cobol", "go"): COBOL_TO_GO_PROMPT,
}


# ── Result Dataclass ─────────────────────────────────────────────────────────

@dataclass
class ModernizationResult:
    success: bool
    source_language: str
    target_language: str
    original_code: str
    modernized_code: str
    hallucination_flags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    llm_response: Optional[LLMResponse] = None
    error: Optional[str] = None


# ── Core Modernizer ───────────────────────────────────────────────────────────

class CodeModernizer:
    def __init__(self, client: Optional[OpenRouterClient] = None):
        self.client = client or OpenRouterClient()

    def modernize(
        self,
        code: str,
        source_language: str,
        target_language: str = "python",
    ) -> ModernizationResult:
        """
        Main entry point. Takes optimized code context (from Teammate 1)
        and returns a modernized version with hallucination checks.
        """
        src = source_language.lower().strip()
        tgt = target_language.lower().strip()

        template = PROMPT_MAP.get((src, tgt))
        if not template:
            return ModernizationResult(
                success=False,
                source_language=src,
                target_language=tgt,
                original_code=code,
                modernized_code="",
                error=f"Unsupported language pair: {src} -> {tgt}. Supported: {list(PROMPT_MAP.keys())}",
            )

        user_prompt = template.format(code=code)
        llm_response = self.client.chat(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        if not llm_response.success:
            return ModernizationResult(
                success=False,
                source_language=src,
                target_language=tgt,
                original_code=code,
                modernized_code="",
                llm_response=llm_response,
                error=llm_response.error,
            )

        modernized_code = self._extract_code_block(llm_response.content, tgt)
        hallucination_flags, warnings = self._check_hallucinations(
            original=code,
            modernized=modernized_code,
            source_lang=src,
        )

        return ModernizationResult(
            success=True,
            source_language=src,
            target_language=tgt,
            original_code=code,
            modernized_code=modernized_code,
            hallucination_flags=hallucination_flags,
            warnings=warnings,
            llm_response=llm_response,
        )

    # ── Private Helpers ──────────────────────────────────────────────────────

    def _extract_code_block(self, raw_output: str, language: str) -> str:
        """Pull code out of markdown fences if present."""
        pattern = rf"```(?:{language})?\s*\n(.*?)```"
        match = re.search(pattern, raw_output, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        # No fences — return cleaned output directly
        return raw_output.strip()

    def _check_hallucinations(
        self, original: str, modernized: str, source_lang: str
    ) -> tuple[list[str], list[str]]:
        """
        Heuristic hallucination detection:
        1. Extract identifiers from original and check they appear in modernized
        2. Flag invented imports / libraries not justified by the input
        3. Flag unexpectedly large output (sign of padding / invention)
        """
        flags = []
        warnings = []

        # ── 1. Identifier preservation check ───────────────────────────────
        original_identifiers = self._extract_identifiers(original, source_lang)
        modernized_lower = modernized.lower()

        missing = []
        for ident in original_identifiers:
            # Allow snake_case conversion: "calculateTotal" -> "calculate_total"
            snake = self._to_snake_case(ident)
            if ident.lower() not in modernized_lower and snake not in modernized_lower:
                missing.append(ident)

        if missing:
            flags.append(
                f"[WARN] Possible hallucination - these identifiers from the original are missing: {', '.join(missing[:5])}"
            )

        # ── 2. Suspicious import check ──────────────────────────────────────
        suspicious_imports = ["tensorflow", "torch", "sklearn", "numpy", "pandas", "flask", "django"]
        for lib in suspicious_imports:
            if lib in modernized_lower and lib not in original.lower():
                flags.append(f"[WARN] Invented import detected: '{lib}' not present in original code")

        # ── 3. Size ratio check ─────────────────────────────────────────────
        ratio = len(modernized) / max(len(original), 1)
        if ratio > 4.0:
            warnings.append(
                f"[WARN] Output is {ratio:.1f}x larger than input - review for padding or invented code"
            )

        # ── 4. Review comment count ─────────────────────────────────────────
        review_comments = re.findall(r"#\s*[WARN]\s*REVIEW", modernized)
        if review_comments:
            warnings.append(
                f"[INFO] LLM flagged {len(review_comments)} section(s) for manual review"
            )

        return flags, warnings

    def _extract_identifiers(self, code: str, language: str) -> list[str]:
        """Rough identifier extraction from legacy code."""
        if language == "cobol":
            # Match COBOL paragraph/section names and data names
            return re.findall(r"\b([A-Z][A-Z0-9-]{2,})\b", code)
        elif language == "java":
            # Match Java method and variable names
            return re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]{2,})\b", code)
        return []

    def _to_snake_case(self, name: str) -> str:
        """Convert camelCase or COBOL-CASE to snake_case."""
        # COBOL-CASE -> cobol_case
        name = name.replace("-", "_").lower()
        # camelCase -> camel_case
        name = re.sub(r"([a-z])([A-Z])", r"\1_\2", name).lower()
        return name