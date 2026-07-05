"""C2 Guardrail Escape — xAI Grok models."""

import os, sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logging"))

from logging_harness import BehaviorLogger
from c2_oai_compat import C2OAIAgent


class C2XAIAgent(C2OAIAgent):
    def __init__(self, model_name: str, logger: BehaviorLogger):
        super().__init__(model_name, logger)
        from openai import OpenAI
        self.client = OpenAI(base_url="https://api.x.ai/v1",
                             api_key=os.environ["XAI_API_KEY"])


if __name__ == "__main__":
    import logging_harness
    logging_harness.RESULTS_DIR = Path(__file__).parent.parent / "results"
    for model in ["grok-3", "grok-3-mini"]:
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, "C2")
        agent = C2XAIAgent(model, logger)
        result = agent.run()
        print(f"\n{model} | escaped={result.bypass_detected} | steps={result.total_steps}")
