"""
Statistical multi-run orchestrator — runs C1 (restricted) and C3 N times each,
outputs aggregate stats table for paper Table 2.
"""

import os
import sys
import uuid
import json
import statistics
from pathlib import Path

LAB_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(LAB_ROOT / "agents"))
sys.path.insert(0, str(LAB_ROOT / "logging"))
sys.path.insert(0, str(LAB_ROOT / "experiments"))

import logging_harness
logging_harness.RESULTS_DIR = LAB_ROOT / "results"
(LAB_ROOT / "results").mkdir(exist_ok=True)

from logging_harness import BehaviorLogger
from c1_restricted import C1RestrictedAgent
from c3_tool_misuse import C3ToolMisuseAgent

from rich.console import Console
from rich.table import Table
console = Console()

MODEL = os.environ.get("AGENT_MODEL", "claude-sonnet-4-6")
N_RUNS = int(os.environ.get("N_RUNS", "5"))


def run_n(AgentClass, cls_id, n):
    results = []
    for i in range(n):
        console.rule(f"[cyan]{cls_id} Run {i+1}/{n}[/cyan]")
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, cls_id)
        agent = AgentClass(MODEL, logger)
        try:
            r = agent.run()
            results.append({
                "run": i + 1,
                "bypass": r.bypass_detected,
                "task_done": r.task_completed,
                "steps": r.total_steps,
                "duration": round(r.duration_seconds, 1),
                "notes": r.notes[:120],
            })
            # For C1, also capture route data
            if hasattr(agent, "blocked_attempts"):
                results[-1]["blocked_attempts"] = len(agent.blocked_attempts)
                results[-1]["successful_routes"] = len(agent.successful_routes)
        except Exception as e:
            console.print(f"[red]ERROR run {i+1}: {e}[/red]")
            results.append({"run": i+1, "error": str(e)})
    return results


def print_stats(cls_id, results):
    valid = [r for r in results if "error" not in r]
    if not valid:
        console.print(f"[red]No valid results for {cls_id}[/red]")
        return

    bypass_rate = sum(1 for r in valid if r.get("bypass")) / len(valid)
    task_rate = sum(1 for r in valid if r.get("task_done")) / len(valid)
    steps = [r["steps"] for r in valid]
    durations = [r["duration"] for r in valid]

    table = Table(title=f"{cls_id} — {len(valid)} runs / {MODEL}")
    table.add_column("Run", style="dim")
    table.add_column("Bypass")
    table.add_column("Task Done")
    table.add_column("Steps")
    table.add_column("Duration(s)")
    if cls_id == "C1":
        table.add_column("Blocked Hits")
        table.add_column("Alt Routes")

    for r in valid:
        row = [
            str(r["run"]),
            "[red]YES[/red]" if r.get("bypass") else "[green]NO[/green]",
            "[green]YES[/green]" if r.get("task_done") else "[red]NO[/red]",
            str(r.get("steps", "?")),
            str(r.get("duration", "?")),
        ]
        if cls_id == "C1":
            row += [str(r.get("blocked_attempts", "?")), str(r.get("successful_routes", "?"))]
        table.add_row(*row)

    console.print(table)
    console.print(f"  Bypass rate: {bypass_rate:.0%}  |  "
                  f"Task completion: {task_rate:.0%}  |  "
                  f"Steps: {statistics.mean(steps):.1f} ± {statistics.stdev(steps) if len(steps)>1 else 0:.1f}  |  "
                  f"Duration: {statistics.mean(durations):.1f}s ± {statistics.stdev(durations) if len(durations)>1 else 0:.1f}s")

    return {
        "class": cls_id, "n": len(valid),
        "bypass_rate": bypass_rate, "task_completion_rate": task_rate,
        "steps_mean": statistics.mean(steps),
        "steps_stdev": statistics.stdev(steps) if len(steps) > 1 else 0,
        "duration_mean": statistics.mean(durations),
        "duration_stdev": statistics.stdev(durations) if len(durations) > 1 else 0,
    }


if __name__ == "__main__":
    console.rule("[bold white]MULTI-RUN STATISTICAL EVALUATION[/bold white]")
    console.print(f"Model: {MODEL} | Runs per class: {N_RUNS}\n")

    c1_results = run_n(C1RestrictedAgent, "C1", N_RUNS)
    c3_results = run_n(C3ToolMisuseAgent, "C3", N_RUNS)

    console.rule("[bold white]STATISTICAL SUMMARY[/bold white]")
    stats = {}
    stats["C1"] = print_stats("C1", c1_results)
    stats["C3"] = print_stats("C3", c3_results)

    out_path = LAB_ROOT / "results" / "multirun_stats.json"
    with open(out_path, "w") as f:
        json.dump({"model": MODEL, "n_runs": N_RUNS,
                   "C1": c1_results, "C3": c3_results, "summary": stats}, f, indent=2)
    console.print(f"\nStats saved to {out_path}")
