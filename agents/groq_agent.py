"""Groq agent — OpenAI-compatible endpoint, same interface as OllamaBaseAgent."""

import os
from openai import OpenAI
from ollama_agent import OllamaBaseAgent

GROQ_BASE = "https://api.groq.com/openai/v1"


class GroqBaseAgent(OllamaBaseAgent):

    def __init__(self, model_name: str, logger, experiment_class: str):
        super().__init__(model_name, logger, experiment_class)
        self.client = OpenAI(base_url=GROQ_BASE, api_key=os.environ["GROQ_API_KEY"])
