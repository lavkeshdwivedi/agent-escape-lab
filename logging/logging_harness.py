"""
Central behavior logger — records all agent actions, bypass attempts, and results.
Outputs structured JSONL for analysis and paper evidence.
"""

import json
import os
import time
from dataclasses import asdict
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()
RESULTS_DIR = Path(os.environ.get("RESULTS_DIR", Path(__file__).parent.parent / "results"))


class BehaviorLogger:

    def __init__(self, session_id: str, experiment_class: str):
        self.session_id = session_id
        self.experiment_class = experiment_class
        self.log_path = RESULTS_DIR / f"{experiment_class}_{session_id}.jsonl"
        self.summary_path = RESULTS_DIR / f"{experiment_class}_{session_id}_summary.json"
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    def log_action(self, action):
        entry = {
            "session_id": self.session_id,
            "experiment_class": self.experiment_class,
            **asdict(action),
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

        # Real-time console output
        color = "red" if action.bypass_indicators else "green"
        status = f"[{color}]BYPASS: {action.bypass_indicators}[/{color}]" if action.bypass_indicators else "[green]OK[/green]"
        console.print(f"  Step {action.action_id} | {action.action_type} | {action.tool_name} | {status}")

    def log_result(self, result):
        data = asdict(result)
        with open(self.summary_path, "w") as f:
            json.dump(data, f, indent=2)

        self._print_summary(result)

    def _print_summary(self, result):
        table = Table(title=f"Experiment {result.experiment_class} — {result.experiment_id}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Model", result.agent_model)
        table.add_row("Task", result.task_description[:80])
        table.add_row("Steps", str(result.total_steps))
        table.add_row("Duration", f"{result.duration_seconds:.1f}s")
        table.add_row("Task Completed", "[green]YES[/green]" if result.task_completed else "[red]NO[/red]")
        table.add_row(
            "Bypass Detected",
            f"[red]YES — {result.bypass_vector}[/red]" if result.bypass_detected else "[green]NO[/green]"
        )
        table.add_row("Notes", result.notes[:100] if result.notes else "—")

        console.print(table)


def aggregate_results(results_dir: str = "/results") -> dict:
    """Aggregate all experiment results into a summary table for paper."""
    summary = {"C1": [], "C2": [], "C3": [], "C4": []}

    for f in Path(results_dir).glob("*_summary.json"):
        with open(f) as fp:
            result = json.load(fp)
        cls = result.get("experiment_class", "unknown")
        if cls in summary:
            summary[cls].append({
                "model": result["agent_model"],
                "bypass": result["bypass_detected"],
                "vector": result.get("bypass_vector", ""),
                "task_done": result["task_completed"],
                "steps": result["total_steps"],
            })

    return summary


def print_aggregate_table():
    summary = aggregate_results()
    for cls, runs in summary.items():
        if not runs:
            continue
        table = Table(title=f"Class {cls} Results")
        table.add_column("Model")
        table.add_column("Bypass?")
        table.add_column("Vector")
        table.add_column("Task Done?")
        table.add_column("Steps")
        for r in runs:
            table.add_row(
                r["model"],
                "[red]YES[/red]" if r["bypass"] else "[green]NO[/green]",
                r["vector"] or "—",
                "[green]YES[/green]" if r["task_done"] else "[red]NO[/red]",
                str(r["steps"]),
            )
        console.print(table)
