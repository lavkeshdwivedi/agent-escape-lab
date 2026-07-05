"""C4 Autonomous Escalation — Claude Opus 4.7 and Haiku 4.5."""

import os, sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logging"))

from logging_harness import BehaviorLogger
from c4_autonomous_escalation import C4AutonomousEscalationAgent


if __name__ == "__main__":
    import logging_harness
    logging_harness.RESULTS_DIR = Path(__file__).parent.parent / "results"
    for model in ["claude-opus-4-7", "claude-haiku-4-5-20251001"]:
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, "C4")
        agent = C4AutonomousEscalationAgent(model, logger)
        result = agent.run()
        print(f"\n{model} | escalated={result.bypass_detected} | steps={result.total_steps}")
