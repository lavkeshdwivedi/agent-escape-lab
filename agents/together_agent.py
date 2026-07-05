"""Together AI agent — uses Together's OpenAI-compatible endpoint."""

import os
from openai import OpenAI
from ollama_agent import OllamaBaseAgent

TOGETHER_BASE = "https://api.together.xyz/v1"


class TogetherBaseAgent(OllamaBaseAgent):

    def __init__(self, model_name: str, logger, experiment_class: str):
        super().__init__(model_name, logger, experiment_class)
        self.client = OpenAI(base_url=TOGETHER_BASE, api_key=os.environ["TOGETHER_API_KEY"])
