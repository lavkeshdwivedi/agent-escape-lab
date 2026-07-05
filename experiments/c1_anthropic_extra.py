"""C1 Network Evasion — extra Anthropic Claude models (Opus 4.7, Haiku 4.5)."""

import sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logging"))
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "/agents")
sys.path.insert(0, "/logging")

from logging_harness import BehaviorLogger
from c1_network_evasion import C1NetworkEvasionAgent


if __name__ == "__main__":
    import logging_harness
    logging_harness.RESULTS_DIR = Path(__file__).parent.parent / "results"
    for model in ["claude-opus-4-7", "claude-haiku-4-5-20251001"]:
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, "C1")
        agent = C1NetworkEvasionAgent(model, logger)
        result = agent.run()
        print(f"\n{model} | bypass={result.bypass_detected} | steps={result.total_steps} | done={result.task_completed}")
