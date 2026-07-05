"""Mistral AI agent — OpenAI-compatible endpoint."""

import os
from openai import OpenAI
from ollama_agent import OllamaBaseAgent

MISTRAL_BASE = "https://api.mistral.ai/v1"


class MistralBaseAgent(OllamaBaseAgent):

    def __init__(self, model_name: str, logger, experiment_class: str):
        super().__init__(model_name, logger, experiment_class)
        self.client = OpenAI(base_url=MISTRAL_BASE, api_key=os.environ["MISTRAL_API_KEY"])
