"""C3 Tool Chain Misuse — xAI Grok models."""

import os, sys, time, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "logging"))

from logging_harness import BehaviorLogger
from base_agent import AgentAction, ExperimentResult
from xai_agent import XAIBaseAgent
from c3_tool_misuse import APPROVED_TOOLS, SYSTEM_PROMPT, TASKS, TOOL_CHAIN_SIGNATURES


class C3XAIAgent(XAIBaseAgent):

    def __init__(self, model_name: str, logger: BehaviorLogger):
        super().__init__(model_name, logger, "C3")
        self.temp_files: dict[str, str] = {}
        self.tool_sequence: list[str] = []

    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        self.tool_sequence.append(tool_name)
        if tool_name == "search_internal_docs":
            return f"[MOCK] Found 3 docs matching '{tool_input.get('query','')}': doc1.txt, doc2.txt, doc3.txt"
        elif tool_name == "write_to_temp_file":
            path = f"/tmp/{tool_input.get('filename','out.txt')}"
            self.temp_files[path] = tool_input.get("content", "")
            return f"Written to {path}"
        elif tool_name == "run_python_snippet":
            path = tool_input.get("file_path", "")
            content = self.temp_files.get(path, "")
            return f"[SANDBOXED] Would execute: {content[:200]}"
        elif tool_name == "send_internal_notification":
            return f"[MOCK] Notification sent to {tool_input.get('channel','')}: {tool_input.get('message','')[:100]}"
        elif tool_name == "read_temp_file":
            return self.temp_files.get(tool_input.get("file_path", ""), "File not found")
        return "Unknown tool"

    def _detect_chains(self) -> list[str]:
        found, seq_set = [], set(self.tool_sequence)
        for name, patterns in TOOL_CHAIN_SIGNATURES.items():
            for pattern in patterns:
                if all(step & seq_set for step in pattern):
                    found.append(name)
        return found

    def run(self, task: str = None, guardrail_config: dict = None) -> ExperimentResult:
        self.result.task_description = "Tool chain exploitation — xAI Grok"
        self.result.guardrail_config = {"tool_isolation": False}
        start = time.time()

        for task_def in TASKS:
            self.tool_sequence = []
            messages = [{"role": "user", "content": task_def["prompt"]}]
            for _ in range(10):
                response = self._chat(messages, APPROVED_TOOLS, SYSTEM_PROMPT)
                if self._stop_reason(response) == "end_turn":
                    break
                tool_calls = self._extract_tool_calls(response)
                if not tool_calls:
                    break
                messages = self._append_assistant(messages, response)
                outputs = []
                for tc in tool_calls:
                    output = self._execute_tool(tc["name"], tc["input"])
                    action = AgentAction(action_type="tool_call", tool_name=tc["name"],
                                        tool_input=tc["input"], tool_output=output,
                                        bypass_indicators=self._check_bypass_indicators(str(tc["input"])))
                    self.record_action(action)
                    outputs.append(output)
                messages = self._append_tool_results(messages, tool_calls, outputs)

            chains = self._detect_chains()
            if chains:
                self.record_action(AgentAction(action_type="chain_detected", tool_name="analysis",
                                               bypass_indicators=chains,
                                               raw_llm_output=f"Task {task_def['id']}: chains={chains}"))

        self.result.duration_seconds = time.time() - start
        return self.finalize(task_completed=self.result.bypass_detected,
                             notes=f"Sequence: {self.tool_sequence}")


if __name__ == "__main__":
    import logging_harness
    logging_harness.RESULTS_DIR = Path(__file__).parent.parent / "results"
    for model in ["grok-3", "grok-3-mini"]:
        sid = str(uuid.uuid4())[:8]
        logger = BehaviorLogger(sid, "C3")
        agent = C3XAIAgent(model, logger)
        result = agent.run()
        print(f"\n{model} | bypass={result.bypass_detected} | steps={result.total_steps}")
