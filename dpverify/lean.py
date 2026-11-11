"""Check Lean source in a restricted local process and audit its verdict."""

from dataclasses import dataclass
import json
import re
import subprocess
import time
from pathlib import Path
from typing import TypedDict

from .toolchain import Toolchain

SANDBOX = Path(__file__).with_name("lean.sb")
FORBIDDEN = re.compile(
    r"(?m)^\s*#|\b(import|export|namespace|open|set_option|axiom|constant|unsafe|partial|"
    r"native_decide|sorry|sorryAx|admit|initialize|run_tac|run_elab|elab|macro|syntax|attribute|IO)\b"
    r"|\+native|\/-|--"
)
AXIOMS = {"propext", "Quot.sound", "Classical.choice"}
LIMITS = """set_option maxRecDepth 32768
set_option maxHeartbeats 15000000
set_option cbv.maxSteps 2000000
"""


class Position(TypedDict):
    line: int
    column: int


class LeanMessage(TypedDict):
    severity: str
    data: str
    pos: Position


@dataclass(frozen=True)
class LeanCheck:
    ok: bool
    diagnostics: str
    seconds: float
    messages: tuple[LeanMessage, ...]

    def verdict_axioms(self, audit_line: int) -> list[str]:
        reports = [message["data"] for message in self.messages
                   if message["severity"] == "information"
                   and message["pos"] == {"line": audit_line, "column": 0}
                   and message["data"].startswith("'HarnessVerdict' ")]
        if not self.ok or len(reports) != 1:
            raise ValueError("Lean did not report exactly one audit at the verdict command.")
        report, = reports
        if report == "'HarnessVerdict' does not depend on any axioms":
            return []
        match = re.fullmatch(r"'HarnessVerdict' depends on axioms: \[([^\]]*)\]", report)
        if not match:
            raise ValueError("Unexpected Lean verdict audit.")
        dependencies = {name.strip() for name in match[1].split(",") if name.strip()}
        if not dependencies <= AXIOMS:
            unapproved = ", ".join(sorted(dependencies - AXIOMS))
            raise ValueError(f"Lean reported an unapproved axiom: {unapproved}")
        return sorted(dependencies)


def put(path: Path, contents: str) -> None:
    path.write_text(contents, encoding="utf-8")


def lean_code(response: str) -> str:
    match = re.fullmatch(r"```(?:lean4?|lean)?\s*\n(.*?)\n```", response.strip(), re.S)
    code = (match[1] if match else response).strip()
    if not code or FORBIDDEN.search(code):
        raise ValueError("Expected Lean declarations without imports, options, comments, or unsafe tactics.")
    return code


def check_lean(
    directory: Path, file: str, *, output: str | None = None, timeout: int = 420, profile: bool = False,
) -> LeanCheck:
    directory = directory.resolve()
    toolchain = Toolchain.from_environment()
    lean, arm = toolchain.lean, toolchain.model_library
    args = [
        "/usr/bin/sandbox-exec", "-f", str(SANDBOX),
        "-D", f"LEAN_HOME={toolchain.lean_home.resolve()}",
        "-D", f"ARM_LIB={arm.resolve()}", "-D", f"WORK={directory}",
        "-D", f"LEAN_BIN={lean.resolve()}",
        str(lean.resolve()), "--json", "-M", "8000", "-j", "2",
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
                                      "LEAN_PATH": f"{directory}:{arm.resolve()}",
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
    return LeanCheck(success, diagnostics or log, round(time.monotonic() - start, 2), tuple(messages))


def require_lean(directory: Path, file: str) -> None:
    result = check_lean(directory, file, output=file.replace(".lean", ".olean"))
    if not result.ok:
        raise ValueError(f"{file} failed in {directory}\n{result.diagnostics[-1500:]}")
