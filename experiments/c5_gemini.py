"""C5 Multi-Agent Trust Exploitation — Gemini models."""

import os, sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logging"))

from logging_harness import BehaviorLogger
from gemini_agent import GeminiBaseAgent
from c5_oai_compat import C5OAIAgent


class C5GeminiAgent(C5OAIAgent, GeminiBaseAgent):
    def __init__(self, model_name: str, logger: BehaviorLogger):
        GeminiBaseAgent.__init__(self, model_name, logger, "C5")
        self.tools_called: list[str] = []
        self.resource_accessed_with_elevation = False
        self.elevated_relay_detected = False


if __name__ == "__main__":
    import logging_harness
    logging_harness.RESULTS_DIR = Path(__file__).parent.parent / "results"
    for model in ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.5-flash"]:
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, "C5")
        agent = C5GeminiAgent(model, logger)
        result = agent.run()
        print(f"\n{model} | bypass={result.bypass_detected} | steps={result.total_steps}")
