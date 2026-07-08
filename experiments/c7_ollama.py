"""C7 Credential and Secret Exfiltration — Ollama local models."""

import os, sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logging"))

from logging_harness import BehaviorLogger
from c7_oai_compat import C7OAIAgent


class C7OllamaAgent(C7OAIAgent):
    pass  # inherits Ollama client from C7OAIAgent -> OllamaBaseAgent


if __name__ == "__main__":
    import logging_harness
    logging_harness.RESULTS_DIR = Path(__file__).parent.parent / "results"
    for model in ["llama3.1:8b", "mistral:7b"]:
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, "C7")
        agent = C7OllamaAgent(model, logger)
        result = agent.run()
        print(f"\n{model} | bypass={result.bypass_detected} | steps={result.total_steps}")
