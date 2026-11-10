"""Run individual roles with the official DeepSeek Harness Python SDK."""

import json
import os
from pathlib import Path
import sys
import time


DEFAULT_MODEL = "deepseek/deepseek-v4.1-flash-1017"
OPENROUTER_URL = "https://openrouter.ai/api/v1"


def model_runner(work, model, endpoint, key, max_tokens, reasoning_effort=None, *, replay=None):
    from deepseek_harness import DeepSeekHarness

    workspace = work / "workspace"
    workspace.mkdir(parents=True)
    # The SDK's minimal profile has a shell by default. The roles return text.
    disabled = (
        "persistent-bash", "persistent-pwsh", "tool-fs", "tool-working-directory",
        "session-log-deepseek", "plugin-package-inventory-deepseek", "llm-deepseek", "mcp-resources",
    )
    patch = [{"id": name, "disabled": True} for name in disabled]
    profile = {"id": model, "contextWindow": 131072}
    if reasoning_effort is not None:
        profile["compat"] = {"thinkingFormat": "openrouter"}
        profile["reasoningEfforts"] = {"off": "none", "low": "low", "high": "high", "max": "max"}
    patch.append({"insert": [{
        "id": "dp-llm",
        "name": "@deepseek-ai/dsh-llm-pi-ai",
        "config": {"providers": {"dp-endpoint": {
            "apiKeyEnv": "DP_HARNESS_MODEL_KEY",
            "baseURL": endpoint,
            "api": "openai-completions",
            "models": [profile],
            "retryPolicy": {"mode": "normal", "maxRetries": 0},
        }}},
    }]})
    interface = "Your only interface is your final text response. You have no shell or file tools. "
    if replay is not None:
        stage, timeout, profile_replay = replay
        server_args = ["-m", "dpverify.replay", str(stage), str(work), str(timeout)]
        if profile_replay:
            server_args.append("--profile")
        patch.append({"insert": [{
            "id": "dp-arm-replay",
            "name": "@deepseek-ai/dsh-mcp-client",
            "config": {
                "serverName": "arm", "transport": "stdio", "command": sys.executable,
                "args": server_args, "failOnStartupError": True,
                "toolCallTimeoutMs": (timeout + 60) * 1000,
                "cwd": str(Path(__file__).resolve().parent.parent),
            },
        }]})
        interface = "Use the provided ARM replay tool through its tool-call interface. You have no shell or file tools. "
    patch_path = work / "model.patch.yml"
    patch_path.write_text(json.dumps(patch), encoding="utf-8")
    return DeepSeekHarness(
        provider="dp-endpoint", model=model, max_tokens=max_tokens,
        reasoning_effort=reasoning_effort,
        cwd=str(workspace), dsh_home=str(work / "home"), profile="sdk-minimal",
        patches=(str(patch_path),),
        request_timeout_seconds=120,
        env={
            "DP_HARNESS_MODEL_KEY": key,
            "DSH_TELEMETRY_MODE": "DISABLED",
            "DSH_SYSTEM_PROMPT": (
                "You are a Lean 4 formalization worker. All inputs are in the prompt. " + interface
                + "Never emit tool-call markup or shell commands. Return the requested Lean artifact directly."
            ),
        },
    )


def credentials(endpoint):
    name = "OPENROUTER_API_KEY" if endpoint.rstrip("/") == OPENROUTER_URL else "DP_HARNESS_MODEL_KEY"
    key = os.getenv(name)
    if not key:
        raise ValueError(f"Set {name} in the terminal before requesting live inference.")
    return key


def ask(run_dir, prompt, model, endpoint, key, max_tokens, reasoning_effort=None, *, replay=None):
    from deepseek_harness.errors import HarnessError

    run_dir.mkdir()
    (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    metadata = {"model": model, "max_tokens": max_tokens, "reasoning_effort": reasoning_effort,
                "started_unix": time.time()}
    start = time.monotonic()
    try:
        with (run_dir / "notifications.jsonl").open("w", encoding="utf-8", buffering=1) as trace:
            def record(notification):
                trace.write(json.dumps({"method": notification.method, "payload": notification.payload}) + "\n")

            with model_runner(run_dir, model, endpoint, key, max_tokens, reasoning_effort, replay=replay) as harness:
                result = harness.run(prompt, session_id="attempt", on_notification=record)
        (run_dir / "response.txt").write_text(result.final_response, encoding="utf-8")
        with (run_dir / "events.jsonl").open("w", encoding="utf-8") as log:
            for event in result.events:
                log.write(json.dumps(event) + "\n")
        metadata["finish_reason"] = result.finish_reason
        metadata["usage"] = [event["data"]["usage"] for event in result.events
                             if event["type"] == "assistant/message" and "usage" in event["data"]]
        if result.finish_reason != "completed" or not result.final_response.strip():
            raise ValueError(f"DeepSeek Harness returned {result.finish_reason}. See {run_dir / 'response.txt'}.")
        return result.final_response.strip()
    except (HarnessError, TimeoutError) as error:
        metadata["error"] = type(error).__name__
        raise ValueError(f"DeepSeek Harness failed with {type(error).__name__}. See {run_dir}.") from error
    finally:
        metadata["model_seconds"] = round(time.monotonic() - start, 2)
        (run_dir / "model.json").write_text(json.dumps(metadata, indent=2) + "\n")
