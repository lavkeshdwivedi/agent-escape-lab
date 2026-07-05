"""C4 Autonomous Escalation — OpenAI models."""

import os, sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logging"))

from logging_harness import BehaviorLogger
from openai import OpenAI
from c4_oai_compat import C4OAIAgent


class C4OpenAIAgent(C4OAIAgent):
    def __init__(self, model_name: str, logger: BehaviorLogger):
        super().__init__(model_name, logger)
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


if __name__ == "__main__":
    import logging_harness
    logging_harness.RESULTS_DIR = Path(__file__).parent.parent / "results"
    for model in ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini", "o4-mini", "o3-mini"]:
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, "C4")
        agent = C4OpenAIAgent(model, logger)
        result = agent.run()
        print(f"\n{model} | escalated={result.bypass_detected} | steps={result.total_steps}")
