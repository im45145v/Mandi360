"""Isolated LLM access (Backboard.io, OpenAI, or any OpenAI-compatible API).

Deterministic analytics never call this module. Only agents.* call it, and
only with small, pre-aggregated evidence bundles (never raw review dumps).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

from dotenv import load_dotenv

LLMClient = Callable[[str, str], str]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


class LLMNotConfiguredError(RuntimeError):
    """Raised when an OpenAI-backed client is requested without an API key."""


def make_openai_client(model: str = "gpt-4o-mini") -> LLMClient:
    """Return a callable(system_prompt, user_prompt) -> str backed by the OpenAI API.

    Requires the OPENAI_API_KEY environment variable. The `openai` package is
    imported lazily so the rest of the codebase has no hard dependency on it.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise LLMNotConfiguredError("OPENAI_API_KEY is not set; cannot create an OpenAI-backed LLM client")

    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=os.environ.get("OPENAI_BASE_URL") or None)

    def call(system_prompt: str, user_prompt: str) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""

    return call


BACKBOARD_DEFAULT_URL = "https://app.backboard.io/api"


def make_backboard_client(
    model: str | None = None, provider: str | None = None, timeout: float = 120.0
) -> LLMClient:
    """Return a callable(system_prompt, user_prompt) -> str backed by Backboard.io.

    Requires BACKBOARD_API_KEY. Optional: BACKBOARD_BASE_URL, BACKBOARD_LLM_PROVIDER,
    BACKBOARD_MODEL. Each call creates a throwaway assistant (system prompt) and
    thread, then sends the user prompt without streaming.
    """
    api_key = os.environ.get("BACKBOARD_API_KEY")
    if not api_key:
        raise LLMNotConfiguredError("BACKBOARD_API_KEY is not set; cannot create a Backboard LLM client")

    import requests

    base_url = os.environ.get("BACKBOARD_BASE_URL", BACKBOARD_DEFAULT_URL).rstrip("/")
    provider = provider or os.environ.get("BACKBOARD_LLM_PROVIDER", "openai")
    model = model or os.environ.get("BACKBOARD_MODEL", "gpt-4o-mini")
    headers = {"X-API-Key": api_key}

    def call(system_prompt: str, user_prompt: str) -> str:
        r = requests.post(
            f"{base_url}/assistants",
            json={"name": "Mandi360", "system_prompt": system_prompt},
            headers=headers,
            timeout=timeout,
        )
        r.raise_for_status()
        assistant_id = r.json()["assistant_id"]
        r = requests.post(f"{base_url}/assistants/{assistant_id}/threads", json={}, headers=headers, timeout=timeout)
        r.raise_for_status()
        thread_id = r.json()["thread_id"]
        r = requests.post(
            f"{base_url}/threads/{thread_id}/messages",
            headers=headers,
            data={
                "content": user_prompt,
                "stream": "false",
                "memory": "off",
                "llm_provider": provider,
                "model_name": model,
            },
            timeout=timeout,
        )
        r.raise_for_status()
        return r.json().get("content") or ""

    return call


def make_llm_client() -> LLMClient:
    """Pick a provider from LLM_PROVIDER (backboard | openai), else by which key is set.

    For other OpenAI-compatible APIs, set OPENAI_API_KEY plus OPENAI_BASE_URL.
    """
    provider = os.environ.get("LLM_PROVIDER", "").lower()
    if not provider:
        provider = "backboard" if os.environ.get("BACKBOARD_API_KEY") else "openai"
    if provider == "backboard":
        return make_backboard_client()
    if provider == "openai":
        return make_openai_client(model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
    raise LLMNotConfiguredError(f"Unknown LLM_PROVIDER '{provider}'; use 'backboard' or 'openai'")
