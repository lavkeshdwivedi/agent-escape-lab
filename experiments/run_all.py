"""
Master experiment runner — runs all 4 attack classes across all configured models.
Produces aggregate results table for paper evidence section.
"""

import os
import sys
import uuid

sys.path.insert(0, "/agents")
sys.path.insert(0, "/logging")

from logging_harness import BehaviorLogger, print_aggregate_table
from c1_network_evasion import C1NetworkEvasionAgent
from c2_guardrail_escape import C2GuardrailEscapeAgent
from c3_tool_misuse import C3ToolMisuseAgent
from c4_autonomous_escalation import C4AutonomousEscalationAgent

from rich.console import Console
console = Console()

MODELS = [
    "claude-sonnet-4-6",
    # "claude-haiku-4-5-20251001",   # uncomment to add
    # "gpt-4o",                       # requires openai key
]

EXPERIMENT_CLASSES = {
    "C1": C1NetworkEvasionAgent,
    "C2": C2GuardrailEscapeAgent,
    "C3": C3ToolMisuseAgent,
    "C4": C4AutonomousEscalationAgent,
}


def run_all(models=MODELS, classes=None):
    if classes is None:
        classes = list(EXPERIMENT_CLASSES.keys())

    total = len(models) * len(classes)
    run = 0

    for model in models:
        for cls_name in classes:
            run += 1
            console.rule(f"[bold cyan]{cls_name} | {model} | Run {run}/{total}[/bold cyan]")

            session_id = str(uuid.uuid4())[:8]
            logger = BehaviorLogger(session_id, cls_name)

            AgentClass = EXPERIMENT_CLASSES[cls_name]
            agent = AgentClass(model, logger)

            try:
                result = agent.run()
                console.print(
                    f"[green]Completed {cls_name}[/green] — "
                    f"bypass={'YES' if result.bypass_detected else 'NO'}, "
                    f"task_done={'YES' if result.task_completed else 'NO'}"
                )
            except Exception as e:
                console.print(f"[red]ERROR in {cls_name}/{model}: {e}[/red]")

    console.rule("[bold white]AGGREGATE RESULTS[/bold white]")
    print_aggregate_table()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--classes", nargs="+", choices=["C1", "C2", "C3", "C4"], default=None)
    parser.add_argument("--model", type=str, default=None)
    args = parser.parse_args()

    models = [args.model] if args.model else MODELS
    run_all(models=models, classes=args.classes)
