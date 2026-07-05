"""C3 Tool Chain Exploitation — new Anthropic models (Fable 5, Sonnet 5, Opus 4.8)."""

import sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logging"))
sys.path.insert(0, str(Path(__file__).parent))

from logging_harness import BehaviorLogger
from c3_tool_misuse import C3ToolMisuseAgent


if __name__ == "__main__":
    import logging_harness
    logging_harness.RESULTS_DIR = Path(__file__).parent.parent / "results"
    for model in ["claude-fable-5", "claude-sonnet-5", "claude-opus-4-8"]:
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, "C3")
        agent = C3ToolMisuseAgent(model, logger)
        result = agent.run()
        print(f"\n{model} | bypass={result.bypass_detected} | steps={result.total_steps} | done={result.task_completed}")
