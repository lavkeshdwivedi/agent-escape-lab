"""OpenRouter client: one OpenAI-compatible endpoint for models from every major provider."""

import os
from openai import OpenAI

OPENROUTER_BASE = "https://openrouter.ai/api/v1"


def openrouter_client() -> OpenAI:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    return OpenAI(
        base_url=OPENROUTER_BASE,
        api_key=api_key,
        default_headers={"X-Title": "agent-escape-lab"},
    )
