"""C5 Multi-Agent Trust Exploitation — Mistral AI models."""

import os, sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logging"))

from logging_harness import BehaviorLogger
from c5_oai_compat import C5OAIAgent


class C5MistralAgent(C5OAIAgent):
    def __init__(self, model_name: str, logger: BehaviorLogger):
        super().__init__(model_name, logger)
        from openai import OpenAI
        self.client = OpenAI(base_url="https://api.mistral.ai/v1",
                             api_key=os.environ["MISTRAL_API_KEY"])


if __name__ == "__main__":
    import logging_harness
    logging_harness.RESULTS_DIR = Path(__file__).parent.parent / "results"
    for model in ["mistral-large-latest", "mistral-small-latest"]:
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, "C5")
        agent = C5MistralAgent(model, logger)
        result = agent.run()
        print(f"\n{model} | bypass={result.bypass_detected} | steps={result.total_steps}")
