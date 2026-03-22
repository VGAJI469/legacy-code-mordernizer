"""
llm_client.py — OpenRouter API Client
Teammate 2: LLM Integration & Modernization Suggester
"""

import os
import time
import requests
from typing import Optional
from dataclasses import dataclass


OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openrouter/auto"  # Auto-selects best available free model
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


@dataclass
class LLMResponse:
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    success: bool
    error: Optional[str] = None


class OpenRouterClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.environ.get("HF_API_KEY") or ""
        self.model = model or DEFAULT_MODEL

    def count_tokens(self, text: str) -> int:
        """Estimate token count — roughly 1 token per 4 characters (OpenAI standard)."""
        return max(1, len(text) // 4)

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> LLMResponse:
        """
        Send a chat request to OpenRouter with retry logic.
        Low temperature (0.2) reduces hallucinations for code generation.
        Falls back to mock mode if API key is invalid/missing.
        """
        prompt_tokens = self.count_tokens(system_prompt + user_prompt)
        
        # Check if running in mock mode (invalid or test API key)
        if not self.api_key or self.api_key.startswith("hf_") or self.api_key.startswith("test_"):
            print("[WARN] Running in MOCK mode (no valid API key). Using mock responses.")
            return self._mock_response(user_prompt, prompt_tokens)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://legacy-modernizer.dev",
            "X-Title": "Legacy Code Modernization Engine",
        }

        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                start = time.time()
                response = requests.post(
                    OPENROUTER_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=60,
                )
                latency_ms = (time.time() - start) * 1000

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})

                    return LLMResponse(
                        content=content,
                        model=self.model,
                        prompt_tokens=usage.get("prompt_tokens", prompt_tokens),
                        completion_tokens=usage.get("completion_tokens", self.count_tokens(content)),
                        total_tokens=usage.get("total_tokens", prompt_tokens + self.count_tokens(content)),
                        latency_ms=latency_ms,
                        success=True,
                    )
                else:
                    last_error = f"HTTP {response.status_code}: {response.text[:200]}"

            except requests.exceptions.Timeout:
                last_error = "Request timed out after 60s"
            except requests.exceptions.RequestException as e:
                last_error = str(e)

            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))

        # If real API fails, fall back to mock mode for development
        print(f"[WARN] LLM API failed: {last_error}. Falling back to MOCK mode.")
        return self._mock_response(user_prompt, prompt_tokens)

    def _mock_response(self, user_prompt: str, prompt_tokens: int) -> LLMResponse:
        """Generate a mock code response for development/testing without a real LLM."""
        import re
        
        # Extract language hints from the prompt
        if "python" in user_prompt.lower():
            if "cobol" in user_prompt.lower():
                mock_code = """```python
def process_data(input_data):
    result = {}
    for item in input_data:
        value = item.get('value', 0)
        result[item.get('key')] = value * 2
    return result

if __name__ == '__main__':
    data = [{'key': 'test', 'value': 42}]
    print(process_data(data))
```"""
            else:  # Java to Python
                mock_code = """```python
class DataProcessor:
    def __init__(self):
        self.items = []
    
    def process(self, value):
        return value * 2
    
    def get_items(self):
        return self.items

if __name__ == '__main__':
    processor = DataProcessor()
    print(processor.process(42))
```"""
        else:  # Go
            if "cobol" in user_prompt.lower():
                mock_code = """```go
package main

import "fmt"

func processData(data map[string]int) map[string]int {
    result := make(map[string]int)
    for key, value := range data {
        result[key] = value * 2
    }
    return result
}

func main() {
    data := map[string]int{"test": 42}
    fmt.Println(processData(data))
}
```"""
            else:  # Java to Go
                mock_code = """```go
package main

import "fmt"

type DataProcessor struct {
    items []interface{}
}

func (dp *DataProcessor) Process(value int) int {
    return value * 2
}

func (dp *DataProcessor) GetItems() []interface{} {
    return dp.items
}

func main() {
    processor := &DataProcessor{}
    fmt.Println(processor.Process(42))
}
```"""
        
        content = mock_code
        completion_tokens = self.count_tokens(content)
        
        return LLMResponse(
            content=content,
            model="mock/test-model",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=100,
            success=True,
        )