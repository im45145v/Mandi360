"""Isolated OpenAI access for agentic reasoning.

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

    client = OpenAI(api_key=api_key)

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
