"""Three-stage OpenDP pilot with DeepSeek Harness and a local Lean gate."""

import argparse
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

from .model import DEFAULT_MODEL, OPENROUTER_URL, ask, credentials

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CASE = ROOT / "cases/opendp-bounded-sum"
CACHE = Path(os.getenv("OPENDP_PILOT_CACHE", Path.home() / "Library/Caches/lean-binary-dp-demo"))
ARM = CACHE / "code-verification/arm64-semantics/Arm64/.lake/build/lib/lean"
LEAN = Path(os.getenv("LEAN_BIN_DIR", CACHE / "lean-4.34.0-darwin_aarch64/bin")) / "lean"
PUBLIC_CASE = (CASE / "brief.txt").read_text()
PROVENANCE = json.loads((CASE / "provenance.json").read_text())
FORBIDDEN = re.compile(
    r"(?m)^\s*#|\b(import|export|namespace|open|set_option|axiom|constant|unsafe|partial|"
    r"native_decide|sorry|admit|initialize|run_tac|run_elab|elab|macro|syntax|attribute|IO)\b"
    r"|\+native|\/-|--"
)
AXIOMS = {"propext", "Quot.sound", "Classical.choice"}
LIMITS = """set_option maxRecDepth 32768
set_option maxHeartbeats 15000000
set_option cbv.maxSteps 2000000
"""
SPEC_CHECKS = """
example : Dataset → Dataset → Nat := symmetricDistance
example : Nat → Nat → Nat := absoluteDifference
example : (Dataset → Option Nat) → (Budget → Option Nat) → Prop := Sensitivity
"""


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path, contents):
    path.write_text(contents, encoding="utf-8")


def check_toolchain():
    lean_version = subprocess.check_output([str(LEAN), "--short-version"], text=True).strip()
    model = CACHE / "code-verification"
    revision = subprocess.check_output(["git", "-C", str(model), "rev-parse", "HEAD"], text=True).strip()
    if lean_version != PROVENANCE["lean"] or revision != PROVENANCE["arm_model_git"]:
        raise ValueError("The Lean or DeepMind ARM model version differs from the pilot's pin.")
    subprocess.run(["git", "-C", str(model), "diff", "--quiet", "HEAD", "--", "arm64-semantics"], check=True)


def lean_code(response):
    match = re.fullmatch(r"```(?:lean4?|lean)?\s*\n(.*?)\n```", response.strip(), re.S)
    code = (match[1] if match else response).strip()
    if not code or FORBIDDEN.search(code):
        raise ValueError("Expected Lean declarations without imports, options, comments, or unsafe tactics.")
    return code


def check_lean(directory, file, *, output=None, timeout=420, profile=False):
    directory = directory.resolve()
    if not LEAN.is_file() or not (ARM / "Arm64/Trusted/ISA/Semantics.olean").is_file():
        raise ValueError("Build the OpenDP pilot's pinned Lean/ARM dependencies first.")
    args = [
        "/usr/bin/sandbox-exec", "-f", str(HERE / "lean.sb"),
        "-D", f"LEAN_HOME={LEAN.parent.parent.resolve()}",
        "-D", f"ARM_LIB={ARM.resolve()}", "-D", f"WORK={directory}",
        "-D", f"LEAN_BIN={LEAN.resolve()}",
        str(LEAN.resolve()), "--json", "-M", "8000", "-j", "2",
    ]
    if output:
        args += ["-o", output]
    if profile:
        args.append("--profile")
    args.append(file)
    start = time.monotonic()
    log_path = directory / f"{file}.log"
    timed_out = False
    with log_path.open("w", encoding="utf-8") as trace:
        try:
            done = subprocess.run(args, cwd=directory, stdout=trace,
                                  stderr=subprocess.STDOUT, timeout=timeout, env={
                                      "LEAN_PATH": f"{directory}:{ARM.resolve()}",
                                      "PATH": "/usr/bin:/bin",
                                  })
            success = done.returncode == 0
        except subprocess.TimeoutExpired:
            trace.write("\nLean timed out.\n")
            success = False
            timed_out = True
    log = log_path.read_text(errors="replace")
    messages = []
    for line in log.splitlines():
        if line.startswith("{"):
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                if not timed_out:
                    raise
    diagnostics = "\n".join(str(m.get("data", "")) for m in messages)
    if timed_out:
        diagnostics = (diagnostics + "\nLean timed out.").lstrip()
    return success, diagnostics or log, round(time.monotonic() - start, 2)


def require_lean(directory, file):
    ok, log, _ = check_lean(directory, file, output=file.replace(".lean", ".olean"))
    if not ok:
        raise ValueError(f"{file} failed in {directory}\n{log[-1500:]}")


def axiom_audit(log):
    if "'HarnessVerdict' does not depend on any axioms" in log:
        return []
    matches = re.findall(r"'HarnessVerdict' depends on axioms: \[([^\]]*)\]", log)
    if len(matches) != 1:
        raise ValueError("Lean did not report exactly one audit for HarnessVerdict.")
    dependencies = {x.strip() for x in matches[0].split(",") if x.strip()}
    if not dependencies <= AXIOMS:
        raise ValueError("Lean reported an unapproved axiom: " + ", ".join(sorted(dependencies - AXIOMS)))
    return sorted(dependencies)


def call_model(args, work, prompt, model, *, replay=None):
    return ask(work, prompt, model, args.endpoint, args.key, args.max_tokens, args.reasoning_effort,
               replay=replay)


def record_run(run, args, role, model):
    settings = {
        "schema_version": 1, "mode": "fixture-replay" if args.fixture_replay else "live",
        "case": "opendp-sized-bounded-sum", "role": role, "model": model,
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
        files = [HERE / "workflow.py", HERE / "model.py", HERE / "lean.sb", CASE / "proof.prompt",
                 CASE / ("proof-replay.prompt" if args.arm_replay else "proof-direct.prompt")]
        if args.arm_replay:
            files.append(HERE / "replay.py")
        settings["harness_sha256"] = {str(path.relative_to(ROOT)): digest(path) for path in files}
    put(run / "experiment.json", json.dumps(settings, indent=2) + "\n")


def draft(args):
    run = args.run.resolve()
    run.mkdir(parents=True)
    record_run(run, args, "spec", args.spec_model)
    shutil.copyfile(CASE / "Inputs.lean", run / "Inputs.lean")
    require_lean(run, "Inputs.lean")
    prompt = (
        (CASE / "spec.prompt").read_text() + "\n" + PUBLIC_CASE
        + "\nINPUTS LEAN DEFINITIONS\n" + (run / "Inputs.lean").read_text()
    )
    feedback = ""
    for attempt in range(1, args.attempts + 1):
        work = run / f"spec-{attempt}"
        try:
            text = call_model(args, work, prompt + feedback, args.spec_model)
            put(run / "Spec.lean", "import Inputs\n\n" + lean_code(text) + "\n" + SPEC_CHECKS)
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


def prepare_machine(run, candidate, *, arm_replay):
    expected = PROVENANCE["fixture_sha256"]
    for name, checksum in expected.items():
        if digest(CASE / name) != checksum:
            raise ValueError(f"Pilot artifact differs from the pinned snapshot: {name}")
    # Assign opaque IDs by the known binary digests. Labels and native test results
    # stay out of the proof prompt.
    binaries = sorted(
        (PROVENANCE["binary_sha256"][side], side)
        for side in ("before", "after")
    )
    checksum, side = binaries[ord(candidate) - ord("A")]
    stage = run / candidate
    stage.mkdir()
    extraction = (CASE / "fixtures/ClosureBytes.lean").read_text()
    selection = [section for section in re.split(r"(?=^def )", extraction, flags=re.M)
                 if section.startswith(f"def {side}_")]
    put(stage / "ClosureBytes.lean", "".join(selection).replace(f"def {side}_", "def binary_"))
    replay = (CASE / "native/ArmReplay.lean").read_text().replace("import Spec", "import Inputs")
    start = replay.index("def beforeLayout")
    end = replay.index("def runSum", start)
    replay = replay[:start] + replay[end:]
    put(stage / "Machine.lean", replay + """
def machineLayout : Replay.VectorLayout :=
  ⟨binary_capacityOffset, binary_pointerOffset, binary_lengthOffset⟩
def machineSum := Replay.sum binary_sum machineLayout
def machineBound := Replay.bound binary_bound binary_capture
""")
    for name in ("Inputs.lean", "Spec.lean"):
        shutil.copyfile(run / name, stage / name)
    for module in ("Inputs", "Spec", "ClosureBytes", "Machine"):
        require_lean(stage, f"{module}.lean")
    output = ""
    if not arm_replay:
        put(stage / "Emulate.lean", """import Machine
#eval (List.finRange 4).map (fun a => (List.finRange 4).map (fun b => machineSum (a, b)))
#eval (List.finRange 5).map machineBound
""")
        ok, output, _ = check_lean(stage, "Emulate.lean", timeout=45)
        if not ok:
            raise ValueError(f"ARM replay failed in {stage}\n{output[-1200:]}")
    put(stage / "binary.json", json.dumps({
        "candidate": candidate, "sha256": checksum, "source_git": PROVENANCE["opendp_git"][side],
        "arm_model_git": PROVENANCE["arm_model_git"], "rust": PROVENANCE["rust"],
        "lean": PROVENANCE["lean"], "closure_bytes_sha256": digest(stage / "ClosureBytes.lean"),
        "machine_sha256": digest(stage / "Machine.lean"),
    }, indent=2) + "\n")
    asm = (CASE / "fixtures" / f"{side}.asm").read_text()
    # Symbols can expose whether the case is old or new. The instruction bytes are sufficient.
    assembly = "\n".join(line.split("<", 1)[0].rstrip() for line in asm.splitlines()
                         if re.match(r"^\s*[0-9a-f]+:", line))
    return stage, output, assembly


def prove_one(args, run, candidate):
    stage, output, assembly = prepare_machine(run, candidate, arm_replay=args.arm_replay)
    instructions = "proof-replay.prompt" if args.arm_replay else "proof-direct.prompt"
    proof_prompt = (CASE / "proof.prompt").read_text().replace(
        "{replay_instructions}", (CASE / instructions).read_text().rstrip(),
    )
    prompt = (
        proof_prompt + "\nFROZEN SPEC\n" + (stage / "Spec.lean").read_text()
        + "\nINPUT TYPE DEFINITIONS\n" + (stage / "Inputs.lean").read_text()
        + "\nMACHINE LEAN API\n" + (stage / "Machine.lean").read_text()
        + ("\nARM REPLAY HINTS\n" + output if output else "") + "\nARM DISASSEMBLY\n" + assembly
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
            target = negation + "_root_.Sensitivity _root_.machineSum _root_.machineBound"
            put(stage / file, imports + "\n" + LIMITS + lean_code(declarations) +
                f"\n\ntheorem HarnessVerdict : {target} := _root_.candidate\n#print axioms HarnessVerdict\n")
            ok, log, elapsed = check_lean(stage, file, timeout=args.lean_timeout, profile=args.lean_profile)
            timings["lean_seconds"] = elapsed
            if not ok:
                raise ValueError(log[-2200:])
            checked = {"candidate": candidate, "status": "refuted" if negation else "proved",
                       "attempt": attempt, **timings, "axioms": axiom_audit(log)}
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


def verify(args):
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
    record_run(run, args, "proof", args.proof_model)
    shutil.copyfile(CASE / "Inputs.lean", run / "Inputs.lean")
    put(run / "Spec.lean", spec)
    put(run / "spec.sha256", args.approve_spec + "\n")
    outcomes = [prove_one(args, run, case) for case in (args.candidate or "AB")]
    put(run / "report.json", json.dumps(outcomes, indent=2) + "\n")
    for outcome in outcomes:
        print(f"{outcome['candidate']}: {outcome['status']}")
    return int(any(outcome["status"] == "unresolved" for outcome in outcomes))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", default=OPENROUTER_URL)
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--max-tokens", type=int, default=8192)
    parser.add_argument("--reasoning-effort", choices=("off", "low", "high", "max"),
                        help="Override the OpenRouter model's default reasoning effort")
    parser.add_argument("--fixture-replay", action="store_true", help=argparse.SUPPRESS)
    commands = parser.add_subparsers(dest="stage", required=True)
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
        args.key = credentials(args.endpoint)
        check_toolchain()
        return draft(args) if args.stage == "draft" else verify(args)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
