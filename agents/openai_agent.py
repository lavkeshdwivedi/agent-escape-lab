"""OpenAI agent — GPT-4o and variants."""

import os
from openai import OpenAI
from ollama_agent import OllamaBaseAgent


class OpenAIBaseAgent(OllamaBaseAgent):

    def __init__(self, model_name: str, logger, experiment_class: str):
        super().__init__(model_name, logger, experiment_class)
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
