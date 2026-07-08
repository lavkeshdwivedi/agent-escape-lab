"""C5 Multi-Agent Trust Exploitation — Groq models."""

import os, sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logging"))

from logging_harness import BehaviorLogger
from c5_oai_compat import C5OAIAgent


class C5GroqAgent(C5OAIAgent):
    def __init__(self, model_name: str, logger: BehaviorLogger):
        super().__init__(model_name, logger)
        from openai import OpenAI
        self.client = OpenAI(base_url="https://api.groq.com/openai/v1",
                             api_key=os.environ["GROQ_API_KEY"])


if __name__ == "__main__":
    import logging_harness
    logging_harness.RESULTS_DIR = Path(__file__).parent.parent / "results"
    for model in ["llama-4-scout", "llama-3.3-70b-versatile",
                  "meta-llama/llama-4-scout-17b-16e-instruct", "qwen/qwen3-32b"]:
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, "C5")
        agent = C5GroqAgent(model, logger)
        result = agent.run()
        print(f"\n{model} | bypass={result.bypass_detected} | steps={result.total_steps}")
