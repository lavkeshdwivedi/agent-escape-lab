"""xAI agent — Grok models via OpenAI-compatible endpoint."""

import os
from openai import OpenAI
from ollama_agent import OllamaBaseAgent

XAI_BASE = "https://api.x.ai/v1"


class XAIBaseAgent(OllamaBaseAgent):

    def __init__(self, model_name: str, logger, experiment_class: str):
        super().__init__(model_name, logger, experiment_class)
        self.client = OpenAI(base_url=XAI_BASE, api_key=os.environ["XAI_API_KEY"])
