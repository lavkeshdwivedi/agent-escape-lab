"""DeepSeek agent — uses DeepSeek's OpenAI-compatible endpoint."""

import os
from openai import OpenAI
from ollama_agent import OllamaBaseAgent

DEEPSEEK_BASE = "https://api.deepseek.com/v1"


class DeepSeekBaseAgent(OllamaBaseAgent):

    def __init__(self, model_name: str, logger, experiment_class: str):
        super().__init__(model_name, logger, experiment_class)
        self.client = OpenAI(base_url=DEEPSEEK_BASE, api_key=os.environ["DEEPSEEK_API_KEY"])
