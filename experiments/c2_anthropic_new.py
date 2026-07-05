"""C2 Guardrail Escape — new Anthropic models (Fable 5, Sonnet 5, Opus 4.8)."""

import sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logging"))
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "/agents")
sys.path.insert(0, "/logging")

from logging_harness import BehaviorLogger
from c2_guardrail_escape import C2GuardrailEscapeAgent


if __name__ == "__main__":
    import logging_harness
    logging_harness.RESULTS_DIR = Path(__file__).parent.parent / "results"
    for model in ["claude-fable-5", "claude-sonnet-5", "claude-opus-4-8"]:
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, "C2")
        agent = C2GuardrailEscapeAgent(model, logger)
        result = agent.run()
        print(f"\n{model} | bypass={result.bypass_detected} | steps={result.total_steps} | done={result.task_completed}")
