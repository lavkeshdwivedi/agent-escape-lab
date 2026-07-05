"""
Ollama-compatible agent base — uses Ollama's OpenAI-compatible endpoint.
Allows running the same experiments against local models (llama3.1:8b, mistral, etc.)
for multi-model comparison without API keys or internet dependency.
"""

import os
import time
from types import SimpleNamespace
from openai import OpenAI, BadRequestError, RateLimitError, InternalServerError
from base_agent import BaseAgent, AgentAction, ExperimentResult

OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")


class OllamaBaseAgent(BaseAgent):

    def __init__(self, model_name: str, logger, experiment_class: str):
        super().__init__(model_name, logger, experiment_class)
        self.client = OpenAI(base_url=OLLAMA_BASE, api_key="ollama")

    def _chat(self, messages: list, tools: list, system: str, max_tokens: int = 2048) -> dict:
        all_messages = [{"role": "system", "content": system}] + messages
        kwargs = {"model": self.model_name, "messages": all_messages, "max_tokens": max_tokens}
        if tools:
            # Convert Anthropic tool format to OpenAI format
            oai_tools = [{"type": "function", "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"],
            }} for t in tools]
            kwargs["tools"] = oai_tools
            kwargs["tool_choice"] = "auto"
        for attempt in range(5):
            try:
                return self.client.chat.completions.create(**kwargs)
            except (RateLimitError, InternalServerError) as e:
                wait = 15 * (2 ** attempt)  # 15, 30, 60, 120, 240s
                print(f"[rate-limit] waiting {wait}s before retry {attempt + 1}/5…")
                time.sleep(wait)
            except BadRequestError as e:
                msg = SimpleNamespace(content=f"[BLOCKED by provider: {e}]", tool_calls=None)
                choice = SimpleNamespace(message=msg, finish_reason="stop")
                return SimpleNamespace(choices=[choice])
        msg = SimpleNamespace(content="[RATE LIMIT: quota exhausted]", tool_calls=None)
        choice = SimpleNamespace(message=msg, finish_reason="stop")
        return SimpleNamespace(choices=[choice])

    def _extract_tool_calls(self, response) -> list:
        msg = response.choices[0].message
        if not msg.tool_calls:
            return []
        result = []
        for tc in msg.tool_calls:
            import json
            try:
                inp = json.loads(tc.function.arguments or "{}")
            except (json.JSONDecodeError, TypeError):
                inp = {}
            result.append({"id": tc.id, "name": tc.function.name, "input": inp})
        return result

    def _get_text(self, response) -> str:
        msg = response.choices[0].message
        return msg.content or ""

    def _stop_reason(self, response) -> str:
        reason = response.choices[0].finish_reason
        if reason == "tool_calls":
            return "tool_use"
        return "end_turn"

    def _append_assistant(self, messages: list, response) -> list:
        msg = response.choices[0].message
        messages.append({"role": "assistant", "content": msg.content, "tool_calls": msg.tool_calls})
        return messages

    def _append_tool_results(self, messages: list, tool_calls: list, outputs: list) -> list:
        import json
        for tc, output in zip(tool_calls, outputs):
            messages.append({"role": "tool", "tool_call_id": tc["id"],
                             "content": output if isinstance(output, str) else json.dumps(output)})
        return messages
