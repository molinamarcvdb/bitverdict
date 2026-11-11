"""Three-stage OpenDP pilot with DeepSeek Harness and a local Lean gate."""

import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import shutil
import subprocess
import sys

from .cases import ROOT, DEFAULT_CASE, Case, available_cases
from .lean import LIMITS, check_lean, lean_code, put, require_lean
from .model import DEFAULT_MODEL, OPENROUTER_URL, ask, credentials
from .toolchain import Toolchain, digest

HERE = Path(__file__).resolve().parent

def call_model(args, work, prompt, model, *, replay=None):
    return ask(work, prompt, model, args.endpoint, args.key, args.max_tokens, args.reasoning_effort,
               replay=replay)


def record_run(run, args, case, role, model):
    settings = {
        "schema_version": 1, "mode": "fixture-replay" if args.fixture_replay else "live",
        "case": case.name, "role": role, "model": model,
        "candidate_order": case.provenance["candidate_order"],
        "endpoint": args.endpoint, "deepseek_harness_sdk": version("deepseek-harness-sdk"),
        "attempts": args.attempts, "max_tokens_per_request": args.max_tokens,
        "reasoning_effort": args.reasoning_effort,
    }
    if role == "proof":
        settings.update(candidate=args.candidate, spec_sha256=args.approve_spec,
                        arm_replay_tool=args.arm_replay, lean_timeout_seconds=args.lean_timeout,
                        lean_profile=args.lean_profile)
        if args.arm_replay:
            settings.update(replay_timeout_seconds=args.replay_timeout, mcp_sdk=version("mcp"))
        files = [HERE / "workflow.py", HERE / "model.py", HERE / "toolchain.py", HERE / "lean.py", HERE / "cases.py",
                 HERE / "lean.sb", case.directory / "proof.prompt",
                 case.directory / ("proof-replay.prompt" if args.arm_replay else "proof-direct.prompt")]
        if args.arm_replay:
            files.append(HERE / "replay.py")
        settings["harness_sha256"] = {str(path.relative_to(ROOT)): digest(path) for path in files}
    put(run / "experiment.json", json.dumps(settings, indent=2) + "\n")


def draft(args, case):
    run = args.run.resolve()
    run.mkdir(parents=True)
    record_run(run, args, case, "spec", args.spec_model)
    shutil.copyfile(case.directory / "Inputs.lean", run / "Inputs.lean")
    require_lean(run, "Inputs.lean")
    prompt = (
        case.read("spec.prompt") + "\n" + case.read("brief.txt")
        + "\nINPUTS LEAN DEFINITIONS\n" + (run / "Inputs.lean").read_text()
    )
    feedback = ""
    for attempt in range(1, args.attempts + 1):
        work = run / f"spec-{attempt}"
        try:
            text = call_model(args, work, prompt + feedback, args.spec_model)
            put(run / "Spec.lean", "import Inputs\n\n" + lean_code(text) + "\n\n" + case.read("SpecChecks.lean"))
            try:
                require_lean(run, "Spec.lean")
            finally:
                shutil.copyfile(run / "Spec.lean", work / "Spec.lean")
                shutil.copyfile(run / "Spec.lean.log", work / "Spec.lean.log")
            put(run / "spec.sha256", digest(run / "Spec.lean") + "\n")
            print(f"Spec ready for review at {run / 'Spec.lean'}")
            print(f"Spec SHA256 {digest(run / 'Spec.lean')}")
            return
        except ValueError as error:
            put(work / "rejected.txt", str(error) + "\n")
            feedback = "\n\nCorrect this previous attempt.\n" + str(error)[-1800:]
            if work.joinpath("response.txt").is_file():
                feedback += "\n\n" + work.joinpath("response.txt").read_text()[-5000:]
    raise ValueError("The spec did not check. See the attempt logs.")


def prove_one(args, case, run, candidate):
    prepared = case.prepare(run, candidate, include_hints=not args.arm_replay)
    stage = prepared.directory
    instructions = "proof-replay.prompt" if args.arm_replay else "proof-direct.prompt"
    proof_prompt = case.read("proof.prompt").replace(
        "{replay_instructions}", case.read(instructions).rstrip(),
    )
    prompt = (
        proof_prompt + "\nFROZEN SPEC\n" + (stage / "Spec.lean").read_text()
        + "\nINPUT TYPE DEFINITIONS\n" + (stage / "Inputs.lean").read_text()
        + "\nMACHINE LEAN API\n" + (stage / "Machine.lean").read_text()
        + ("\nARM REPLAY HINTS\n" + prepared.hints if prepared.hints else "") + "\nARM DISASSEMBLY\n" + prepared.assembly
    )
    replay = (stage, args.replay_timeout, args.lean_profile) if args.arm_replay else None
    feedback = ""
    for attempt in range(1, args.attempts + 1):
        print(f"{candidate}: proof attempt {attempt}/{args.attempts}", flush=True)
        work = stage / f"proof-{attempt}"
        timings = {"lean_seconds": 0}
        try:
            text = call_model(args, work, prompt + feedback, args.proof_model, replay=replay)
            imports = "import Spec\nimport Machine\n"
            replay_result = work / "replay-result.json"
            if args.arm_replay and replay_result.is_file():
                facts = json.loads(replay_result.read_text())
                timings["replay_status"] = facts["status"]
                timings["replay_cache_hit"] = facts["cached"]
                for key in ("evaluation_seconds", "certificate_seconds"):
                    if key in facts:
                        timings[f"replay_{key}"] = facts[key]
                if facts["status"] == "checked":
                    imports += "import ReplayFacts\n"
            if text == "UNKNOWN":
                break
            verdict, _, declarations = text.partition("\n")
            if verdict not in {"PROVE", "REFUTE"}:
                raise ValueError("The first line must be PROVE, REFUTE, or UNKNOWN.")
            negation = "¬ " if verdict == "REFUTE" else ""
            file = f"Attempt{attempt}.lean"
            target = negation + case.target
            source = (imports + "\n" + LIMITS + lean_code(declarations)
                      + f"\n\ntheorem HarnessVerdict : {target} := _root_.candidate\n"
                      + "#print axioms HarnessVerdict\n")
            put(stage / file, source)
            result = check_lean(stage, file, timeout=args.lean_timeout, profile=args.lean_profile)
            timings["lean_seconds"] = result.seconds
            if not result.ok:
                raise ValueError(result.diagnostics[-2200:])
            checked = {"candidate": candidate, "status": "refuted" if negation else "proved",
                       "attempt": attempt, **timings,
                       "axioms": result.verdict_axioms(len(source.splitlines()))}
            put(stage / "verdict.json", json.dumps(checked, indent=2) + "\n")
            return checked
        except ValueError as error:
            put(stage / f"rejected-{attempt}.json", json.dumps({"diagnostic": str(error), **timings}))
            previous = work / "response.txt"
            feedback = "\n\nRepair the previous attempt using these diagnostics.\n" + str(error)[-2200:]
            if previous.is_file():
                feedback += "\n\n" + previous.read_text()[-9000:]
    checked = {"candidate": candidate, "status": "unresolved"}
    put(stage / "verdict.json", json.dumps(checked, indent=2) + "\n")
    return checked


def verify(args, case):
    approved = args.run.resolve() / "Spec.lean"
    spec_bytes = approved.read_bytes()
    if hashlib.sha256(spec_bytes).hexdigest() != args.approve_spec:
        raise ValueError("Spec SHA256 differs from the reviewed version.")
    spec = spec_bytes.decode()
    header, _, body = spec.partition("\n")
    if header != "import Inputs":
        raise ValueError("Expected the draft's Inputs import.")
    lean_code(body)
    run = args.out.resolve()
    run.mkdir(parents=True)
    record_run(run, args, case, "proof", args.proof_model)
    shutil.copyfile(case.directory / "Inputs.lean", run / "Inputs.lean")
    put(run / "Spec.lean", spec)
    put(run / "spec.sha256", args.approve_spec + "\n")
    outcomes = [prove_one(args, case, run, candidate) for candidate in (args.candidate or "AB")]
    put(run / "report.json", json.dumps(outcomes, indent=2) + "\n")
    for outcome in outcomes:
        print(f"{outcome['candidate']}: {outcome['status']}")
    return int(any(outcome["status"] == "unresolved" for outcome in outcomes))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", default=DEFAULT_CASE, choices=available_cases())
    parser.add_argument("--endpoint", default=OPENROUTER_URL)
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--max-tokens", type=int, default=8192)
    parser.add_argument("--reasoning-effort", choices=("off", "low", "high", "max"),
                        help="Override the OpenRouter model's default reasoning effort")
    parser.add_argument("--fixture-replay", action="store_true", help=argparse.SUPPRESS)
    commands = parser.add_subparsers(dest="stage", required=True)
    commands.add_parser("setup", help="Install pinned Lean and ARM64 model dependencies")
    spec = commands.add_parser("draft")
    spec.add_argument("run", type=Path)
    spec.add_argument("--spec-model", default=DEFAULT_MODEL)
    proof = commands.add_parser("verify")
    proof.add_argument("run", type=Path)
    proof.add_argument("--approve-spec", required=True)
    proof.add_argument("--out", type=Path, required=True)
    proof.add_argument("--proof-model", default=DEFAULT_MODEL)
    proof.add_argument("--candidate", choices=("A", "B"))
    proof.add_argument("--lean-timeout", type=int, default=420)
    proof.add_argument("--lean-profile", action="store_true", help="Save Lean's per-declaration profile")
    proof.add_argument("--arm-replay", action="store_true", help="Give the proof agent the ARM replay tool")
    proof.add_argument("--replay-timeout", type=int, default=420, help="Wall-time limit for replay certificates")
    args = parser.parse_args()
    if args.attempts < 1 or args.max_tokens < 1:
        parser.error("attempts and max-tokens must be positive")
    if args.stage == "verify" and (args.lean_timeout < 1 or args.replay_timeout < 1):
        parser.error("Lean and replay timeouts must be positive")
    if args.reasoning_effort and args.endpoint.rstrip("/") != OPENROUTER_URL:
        parser.error("--reasoning-effort currently configures the OpenRouter endpoint")
    try:
        if args.stage == "setup":
            Toolchain.from_environment().install()
            return 0
        args.key = credentials(args.endpoint)
        case = Case.load(args.case)
        if args.stage == "verify" and args.arm_replay and not case.supports_replay:
            raise ValueError(f"The ARM replay tool is unavailable for {case.name}.")
        Toolchain.from_environment().require()
        return draft(args, case) if args.stage == "draft" else verify(args, case)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
