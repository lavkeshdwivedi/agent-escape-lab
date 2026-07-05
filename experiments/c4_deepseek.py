"""C4 Autonomous Escalation — DeepSeek models."""

import os, sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logging"))

from logging_harness import BehaviorLogger
from c4_oai_compat import C4OAIAgent


class C4DeepSeekAgent(C4OAIAgent):
    def __init__(self, model_name: str, logger: BehaviorLogger):
        super().__init__(model_name, logger)
        from openai import OpenAI
        self.client = OpenAI(base_url="https://api.deepseek.com/v1",
                             api_key=os.environ["DEEPSEEK_API_KEY"])


if __name__ == "__main__":
    import logging_harness
    logging_harness.RESULTS_DIR = Path(__file__).parent.parent / "results"
    for model in ["deepseek-chat", "deepseek-reasoner"]:
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, "C4")
        agent = C4DeepSeekAgent(model, logger)
        result = agent.run()
        print(f"\n{model} | escalated={result.bypass_detected} | steps={result.total_steps}")
