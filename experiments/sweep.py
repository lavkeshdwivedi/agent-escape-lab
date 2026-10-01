"""
Model sweep: run any of C1-C7 against any list of models through one OpenAI-compatible endpoint.

Reuses the Ollama agent classes for each category and swaps the client, so a new
model needs no new per-provider file.

    python experiments/sweep.py --provider ollama --models qwen3:8b llama3.2:3b
    python experiments/sweep.py --provider openrouter --models anthropic/claude-sonnet-5.5 --runs 3
    python experiments/sweep.py --provider openrouter --models-file models.txt --classes C5 C6 C7

Each run appends one row to results/sweep.csv; per-step logs go to results/*.jsonl as usual.
"""

import argparse
import csv
import sys
import time
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path

LAB_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(LAB_ROOT / "agents"))
sys.path.insert(0, str(LAB_ROOT / "logging"))
sys.path.insert(0, str(LAB_ROOT / "experiments"))

import logging_harness
logging_harness.RESULTS_DIR = LAB_ROOT / "results"
logging_harness.RESULTS_DIR.mkdir(exist_ok=True)
from logging_harness import BehaviorLogger

from c1_ollama import C1OllamaAgent
from c2_ollama import C2OllamaAgent
from c3_ollama import C3OllamaAgent
from c4_ollama import C4OllamaAgent
from c5_ollama import C5OllamaAgent
from c6_ollama import C6OllamaAgent
from c7_ollama import C7OllamaAgent

AGENTS = {
    "C1": C1OllamaAgent, "C2": C2OllamaAgent, "C3": C3OllamaAgent, "C4": C4OllamaAgent,
    "C5": C5OllamaAgent, "C6": C6OllamaAgent, "C7": C7OllamaAgent,
}
OUT = logging_harness.RESULTS_DIR / "sweep.csv"
FIELDS = ["timestamp", "provider", "model", "category", "run", "session_id", "bypass_detected",
          "task_completed", "total_steps", "duration_s", "error", "notes"]


def make_agent(cls_id, provider, model, logger):
    agent = AGENTS[cls_id](model, logger)
    if provider == "openrouter":
        from openrouter_agent import openrouter_client
        agent.client = openrouter_client()
    return agent


def write_row(row):
    new = not OUT.exists()
    with OUT.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", choices=["ollama", "openrouter"], required=True)
    ap.add_argument("--models", nargs="*", default=[])
    ap.add_argument("--models-file", help="one model id per line; # comments allowed")
    ap.add_argument("--classes", nargs="*", default=list(AGENTS))
    ap.add_argument("--runs", type=int, default=1)
    args = ap.parse_args()

    models = list(args.models)
    if args.models_file:
        for line in Path(args.models_file).read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                models.append(line)
    if not models:
        ap.error("no models given")

    for model in models:
        for cls_id in args.classes:
            for run in range(1, args.runs + 1):
                sid = str(uuid.uuid4())[:8]
                row = {"timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       "provider": args.provider, "model": model, "category": cls_id,
                       "run": run, "session_id": sid}
                start = time.time()
                try:
                    agent = make_agent(cls_id, args.provider, model, BehaviorLogger(sid, cls_id))
                    r = agent.run()
                    row.update(bypass_detected=r.bypass_detected, task_completed=r.task_completed,
                               total_steps=r.total_steps, notes=(r.notes or "")[:200])
                except Exception as e:
                    row.update(error=f"{type(e).__name__}: {e}"[:300])
                    traceback.print_exc()
                row["duration_s"] = round(time.time() - start, 1)
                write_row(row)
                print(f"{model} | {cls_id} run {run} | bypass={row.get('bypass_detected')} "
                      f"| steps={row.get('total_steps')} | {row.get('error', '')}", flush=True)


if __name__ == "__main__":
    main()
