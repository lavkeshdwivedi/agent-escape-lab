"""
Compiles final statistics from all experiment runs and updates the paper tables.
Run this once multi_run.py and Mistral experiments are complete.
"""

import json
import glob
import statistics
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse

LAB_ROOT = Path(__file__).parent
RESULTS = LAB_ROOT / "results"


def load_all_runs(cls_id, model_filter=None):
    runs = []
    for f in sorted(RESULTS.glob(f"{cls_id}_*_summary.json")):
        with open(f) as fp:
            r = json.load(fp)
        if model_filter and r.get("agent_model", "") != model_filter:
            continue
        base = str(f).replace("_summary.json", "")
        jsonl = base + ".jsonl"
        routes = []
        chains = []
        if Path(jsonl).exists():
            with open(jsonl) as fp:
                for line in fp:
                    l = json.loads(line)
                    if l.get("action_type") == "tool_call" and l.get("tool_name") == "http_request":
                        out = l.get("tool_output", "")
                        url = l.get("tool_input", {}).get("url", "")
                        if "HTTP 200" in out and url:
                            try:
                                routes.append(urlparse(url).netloc)
                            except Exception:
                                pass
                    if l.get("action_type") == "chain_detected":
                        chains.extend(l.get("bypass_indicators", []))
        entry = {
            "model": r.get("agent_model", "?"),
            "steps": r["total_steps"],
            "duration": r["duration_seconds"],
            "done": r["task_completed"],
            "bypass": r["bypass_detected"],
            "bypass_vector": r.get("bypass_vector", ""),
            "unique_routes": len(set(routes)),
            "chains": list(set(chains)),
        }
        # Skip rate-limit failures (1 step, not done, took >400s)
        if entry["steps"] <= 1 and not entry["done"] and entry["duration"] > 400:
            continue
        runs.append(entry)
    return runs


def stats(values):
    if not values:
        return "N/A", "N/A"
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0
    return f"{mean:.1f}", f"{sd:.1f}"


def aggregate_domains(cls_id):
    domain_hits = Counter()
    for f in sorted(RESULTS.glob(f"{cls_id}_*.jsonl")):
        with open(f) as fp:
            for line in fp:
                l = json.loads(line)
                if l.get("action_type") == "tool_call" and l.get("tool_name") == "http_request":
                    out = l.get("tool_output", "")
                    url = l.get("tool_input", {}).get("url", "")
                    if "HTTP 200" in out and url:
                        try:
                            domain_hits[urlparse(url).netloc] += 1
                        except Exception:
                            pass
    return domain_hits


def print_table(cls_id, models):
    print(f"\n{'='*60}")
    print(f"  CLASS {cls_id} — Statistical Summary")
    print(f"{'='*60}")
    for model in models:
        runs = load_all_runs(cls_id, model)
        if not runs:
            print(f"  {model}: no runs found")
            continue
        br = sum(1 for r in runs if r["bypass"]) / len(runs)
        tcr = sum(1 for r in runs if r["done"]) / len(runs)
        steps_m, steps_s = stats([r["steps"] for r in runs])
        dur_m, dur_s = stats([r["duration"] for r in runs])
        routes_m, routes_s = stats([r["unique_routes"] for r in runs if r["unique_routes"] > 0]) if any(r["unique_routes"] > 0 for r in runs) else ("0", "0")
        chains = [c for r in runs for c in r["chains"]]
        print(f"\n  Model: {model} ({len(runs)} runs)")
        print(f"    Bypass rate:    {br:.0%}")
        print(f"    Task complete:  {tcr:.0%}")
        print(f"    Steps:          {steps_m} ± {steps_s}")
        print(f"    Duration:       {dur_m}s ± {dur_s}s")
        if cls_id == "C1":
            print(f"    Routes/run:     {routes_m} ± {routes_s}")
        if cls_id == "C3" and chains:
            print(f"    Chains found:   {', '.join(set(chains))}")


if __name__ == "__main__":
    models = [
        # Anthropic (new generation)
        "claude-fable-5",
        "claude-sonnet-5",
        "claude-opus-4-8",
        # Anthropic (legacy)
        "claude-sonnet-4-6",
        "claude-opus-4-7",
        "claude-haiku-4-5-20251001",
        # OpenAI
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4.1",
        "gpt-4.1-mini",
        "o4-mini",
        "o3-mini",
        # DeepSeek
        "deepseek-chat",
        "deepseek-reasoner",
        # Google Gemini
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-3-flash-preview",
        "gemini-3.5-flash",
        # xAI
        "grok-3",
        "grok-3-mini",
        # Mistral AI
        "mistral-large-latest",
        "mistral-small-latest",
        # Groq / Meta LLaMA / Qwen / OpenAI OSS
        "llama-3.3-70b-versatile",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "qwen/qwen3-32b",
        "qwen/qwen3.6-27b",
        "openai/gpt-oss-120b",
        # Ollama local
        "llama3.1:8b",
        "mistral:7b",
    ]

    print_table("C1", models)
    print_table("C3", models)
    print_table("C2", models)
    print_table("C4", models)

    print(f"\n{'='*60}")
    print("  TOP ALTERNATIVE DOMAINS (C1, all runs, all models)")
    print(f"{'='*60}")
    domains = aggregate_domains("C1")
    for domain, count in domains.most_common(15):
        print(f"  {count:3}x  {domain}")

    # Save final stats JSON
    output = {}
    for cls_id in ["C1", "C3", "C2", "C4"]:
        output[cls_id] = {}
        for model in models:
            runs = load_all_runs(cls_id, model)
            if runs:
                output[cls_id][model] = {
                    "n": len(runs),
                    "bypass_rate": sum(1 for r in runs if r["bypass"]) / len(runs),
                    "task_completion_rate": sum(1 for r in runs if r["done"]) / len(runs),
                    "steps_mean": statistics.mean([r["steps"] for r in runs]),
                    "steps_sd": statistics.stdev([r["steps"] for r in runs]) if len(runs) > 1 else 0,
                    "duration_mean": statistics.mean([r["duration"] for r in runs]),
                    "duration_sd": statistics.stdev([r["duration"] for r in runs]) if len(runs) > 1 else 0,
                }

    out_path = RESULTS / "final_stats.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nFinal stats saved to {out_path}")
