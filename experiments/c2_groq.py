"""C2 Guardrail Escape — Groq models."""

import os, sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logging"))

from logging_harness import BehaviorLogger
from c2_oai_compat import C2OAIAgent


class C2GroqAgent(C2OAIAgent):
    def __init__(self, model_name: str, logger: BehaviorLogger):
        super().__init__(model_name, logger)
        from openai import OpenAI
        self.client = OpenAI(base_url="https://api.groq.com/openai/v1",
                             api_key=os.environ["GROQ_API_KEY"])


if __name__ == "__main__":
    import logging_harness
    logging_harness.RESULTS_DIR = Path(__file__).parent.parent / "results"
    for model in ["llama-3.3-70b-versatile",
                  "meta-llama/llama-4-scout-17b-16e-instruct",
                  "qwen/qwen3-32b", "qwen/qwen3.6-27b", "openai/gpt-oss-120b"]:
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, "C2")
        agent = C2GroqAgent(model, logger)
        result = agent.run()
        print(f"\n{model} | escaped={result.bypass_detected} | steps={result.total_steps}")
