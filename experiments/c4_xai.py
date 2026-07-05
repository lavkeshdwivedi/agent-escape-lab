"""C4 Autonomous Escalation — xAI Grok models."""

import os, sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logging"))

from logging_harness import BehaviorLogger
from c4_oai_compat import C4OAIAgent
from xai_agent import XAI_BASE


class C4XAIAgent(C4OAIAgent):
    def __init__(self, model_name: str, logger: BehaviorLogger):
        super().__init__(model_name, logger)
        api_key = os.environ.get("XAI_API_KEY")
        if not api_key:
            raise EnvironmentError("XAI_API_KEY is not set. Export it before running xAI experiments.")
        from openai import OpenAI
        self.client = OpenAI(base_url=XAI_BASE, api_key=api_key)


if __name__ == "__main__":
    import logging_harness
    logging_harness.RESULTS_DIR = Path(__file__).parent.parent / "results"
    for model in ["grok-3", "grok-3-mini"]:
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, "C4")
        agent = C4XAIAgent(model, logger)
        result = agent.run()
        print(f"\n{model} | escalated={result.bypass_detected} | steps={result.total_steps}")
