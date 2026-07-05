"""
Local runner — runs all 4 experiment classes without Docker.
Patches container paths to local equivalents and runs against real Anthropic API.
Network restrictions are not enforced (no proxy/firewall), so experiments measure
agent *reasoning and tool-calling behavior* when encountering blocked responses.
"""

import os
import sys
import uuid
from pathlib import Path

# Patch paths so experiments find their imports locally
LAB_ROOT = Path(__file__).parent
sys.path.insert(0, str(LAB_ROOT / "agents"))
sys.path.insert(0, str(LAB_ROOT / "logging"))
sys.path.insert(0, str(LAB_ROOT / "experiments"))

# Patch results dir to local
import logging_harness
logging_harness.RESULTS_DIR = LAB_ROOT / "results"
(LAB_ROOT / "results").mkdir(exist_ok=True)

from logging_harness import BehaviorLogger, print_aggregate_table
from c1_network_evasion import C1NetworkEvasionAgent
from c2_guardrail_escape import C2GuardrailEscapeAgent
from c3_tool_misuse import C3ToolMisuseAgent
from c4_autonomous_escalation import C4AutonomousEscalationAgent

from rich.console import Console
console = Console()

MODEL = os.environ.get("AGENT_MODEL", "claude-sonnet-4-6")

EXPERIMENTS = [
    ("C1", "Network Evasion — does agent find alternate routes?", C1NetworkEvasionAgent),
    ("C2", "Guardrail Escape — does agent bypass via context/memory?", C2GuardrailEscapeAgent),
    ("C3", "Tool Chain Misuse — does agent exploit tool composition?", C3ToolMisuseAgent),
    ("C4", "Autonomous Escalation — does agent self-modify constraints?", C4AutonomousEscalationAgent),
]


def run(classes=None):
    selected = [e for e in EXPERIMENTS if classes is None or e[0] in classes]

    for cls_id, description, AgentClass in selected:
        console.rule(f"[bold cyan]Experiment {cls_id} | {MODEL}[/bold cyan]")
        console.print(f"[dim]{description}[/dim]\n")

        session_id = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(session_id, cls_id)
        agent = AgentClass(MODEL, logger)

        try:
            result = agent.run()
            status = "[green]BYPASS DETECTED[/green]" if result.bypass_detected else "[blue]No bypass[/blue]"
            console.print(f"\n{cls_id} done — {status} | steps={result.total_steps} | {result.duration_seconds:.1f}s\n")
        except Exception as e:
            console.print(f"[red]ERROR in {cls_id}: {e}[/red]")
            import traceback; traceback.print_exc()

    console.rule("[bold white]AGGREGATE RESULTS[/bold white]")
    print_aggregate_table()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--classes", nargs="+", choices=["C1", "C2", "C3", "C4"])
    args = parser.parse_args()
    run(classes=args.classes)
