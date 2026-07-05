"""C2 Guardrail Escape — Ollama local models."""

import os, sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logging"))

from logging_harness import BehaviorLogger
from c2_oai_compat import C2OAIAgent


class C2OllamaAgent(C2OAIAgent):
    pass  # inherits Ollama client from C2OAIAgent -> OllamaBaseAgent


if __name__ == "__main__":
    import logging_harness
    logging_harness.RESULTS_DIR = Path(__file__).parent.parent / "results"
    for model in ["llama3.1:8b", "mistral:7b"]:
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, "C2")
        agent = C2OllamaAgent(model, logger)
        result = agent.run()
        print(f"\n{model} | escaped={result.bypass_detected} | steps={result.total_steps}")
