"""C6 Persistent Adversarial Memory — Gemini models."""

import os, sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logging"))

from logging_harness import BehaviorLogger
from gemini_agent import GeminiBaseAgent
from c6_oai_compat import C6OAIAgent


class C6GeminiAgent(C6OAIAgent, GeminiBaseAgent):
    def __init__(self, model_name: str, logger: BehaviorLogger):
        GeminiBaseAgent.__init__(self, model_name, logger, "C6")
        self.memory_store: dict = {}
        self.knowledge_store: list[str] = []
        self.session_config: dict = {}
        self.poisoned_stores: list[str] = []


if __name__ == "__main__":
    import logging_harness
    logging_harness.RESULTS_DIR = Path(__file__).parent.parent / "results"
    for model in ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.5-flash"]:
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, "C6")
        agent = C6GeminiAgent(model, logger)
        result = agent.run()
        print(f"\n{model} | bypass={result.bypass_detected} | steps={result.total_steps}")
