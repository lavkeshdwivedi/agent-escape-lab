"""Gemini agent — uses Google's OpenAI-compatible endpoint."""

import os
import time
from openai import OpenAI
from ollama_agent import OllamaBaseAgent

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/openai/"
_MIN_INTERVAL = 30.0  # conservative: avoids exponential backoff hell


class GeminiBaseAgent(OllamaBaseAgent):

    def __init__(self, model_name: str, logger, experiment_class: str):
        super().__init__(model_name, logger, experiment_class)
        self.client = OpenAI(base_url=GEMINI_BASE, api_key=os.environ.get("GEMINI_API_KEY_BILLED") or os.environ["GEMINI_API_KEY"])
        self._last_call = 0.0

    def _chat(self, messages: list, tools: list, system: str, max_tokens: int = 2048):
        wait = _MIN_INTERVAL - (time.time() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        result = super()._chat(messages, tools, system, max_tokens)
        self._last_call = time.time()
        return result
