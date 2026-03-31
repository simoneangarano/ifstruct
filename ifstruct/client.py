from __future__ import annotations

import time
from dataclasses import dataclass

import requests


@dataclass
class CompletionResult:
    text: str
    latency_ms: float


def _chat_completions_url(base_url: str) -> str:
    normalized = base_url.rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized
    return normalized + "/chat/completions"


def chat_completion(
    *,
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    max_tokens: int = 8000,
    temperature: float = 0.0,
    timeout: float = 120.0,
    max_retries: int = 40,
    retry_delay: float = 30.0,
) -> CompletionResult:
    """Call an OpenAI-compatible chat completions endpoint."""
    url = _chat_completions_url(base_url)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            start = time.perf_counter()
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            latency_ms = (time.perf_counter() - start) * 1000.0
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                raise ValueError(f"API error: {data['error']}")
            return CompletionResult(
                text=data["choices"][0]["message"]["content"],
                latency_ms=latency_ms,
            )
        except Exception as exc:  # pragma: no cover - network failure path
            last_error = exc
            if attempt < max_retries:
                time.sleep(retry_delay)

    assert last_error is not None
    raise last_error
