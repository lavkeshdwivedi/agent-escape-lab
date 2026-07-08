"""C7 Credential and Secret Exfiltration — Gemini models."""

import os, sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logging"))

from logging_harness import BehaviorLogger
from gemini_agent import GeminiBaseAgent
from c7_oai_compat import C7OAIAgent


class C7GeminiAgent(C7OAIAgent, GeminiBaseAgent):
    def __init__(self, model_name: str, logger: BehaviorLogger):
        GeminiBaseAgent.__init__(self, model_name, logger, "C7")
        self.credentials_harvested: list[str] = []
        self.exfil_attempts: list[str] = []
        self.config_harvested = False


if __name__ == "__main__":
    import logging_harness
    logging_harness.RESULTS_DIR = Path(__file__).parent.parent / "results"
    for model in ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.5-flash"]:
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, "C7")
        agent = C7GeminiAgent(model, logger)
        result = agent.run()
        print(f"\n{model} | bypass={result.bypass_detected} | steps={result.total_steps}")
