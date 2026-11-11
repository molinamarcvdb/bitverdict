"""Expose kernel-checked finite ARM replay facts to the proof agent."""

import argparse
import json
from pathlib import Path
import shutil
import time

from mcp.server.fastmcp import FastMCP

from .lean import LIMITS, check_lean, put
from .toolchain import digest


DATA = """import Machine
import Lean.Data.Json.FromToJson

#eval IO.println (Lean.toJson ((List.finRange 4).map (fun a =>
  (List.finRange 4).map (fun b => machineSum (a, b))))).compress
#eval IO.println (Lean.toJson ((List.finRange 5).map machineBound)).compress
"""
API = """def ARMReplay.sum (x : Dataset) : Option Nat
def ARMReplay.bound (d : Budget) : Option Nat
theorem ARMReplay.sum_eq (x : Dataset) : machineSum x = ARMReplay.sum x
theorem ARMReplay.bound_eq (d : Budget) : machineBound d = ARMReplay.bound d"""


def literal(value):
    if value is None:
        return "none"
    if type(value) is not int or value < 0:
        raise ValueError("Expected a nonnegative integer or null from ARM replay.")
    return f"some {value}"


def facts_source(sums, bounds):
    if not isinstance(sums, list) or len(sums) != 4 or any(
        not isinstance(row, list) or len(row) != 4 for row in sums
    ) or not isinstance(bounds, list) or len(bounds) != 5:
        raise ValueError("ARM replay returned an unexpected table shape.")
    sum_cells = [literal(value) for row in sums for value in row]
    bound_cells = [literal(value) for value in bounds]
    declarations = [
        "import Machine\n", LIMITS, "namespace ARMReplay\n",
        "def sum (x : Dataset) : Option Nat :=\n"
        f"  ([{', '.join(sum_cells)}][x.1.val * 4 + x.2.val]?).getD none",
        "def bound (d : Budget) : Option Nat :=\n"
        f"  ([{', '.join(bound_cells)}][d.val]?).getD none",
    ]
    declarations.extend([
        """private theorem sum_checked :
    (List.finRange 4).all (fun a => (List.finRange 4).all (fun b =>
      decide (machineSum (a, b) = sum (a, b)))) = true := by cbv""",
        """theorem sum_eq (x : Dataset) : machineSum x = sum x := by
  rcases x with ⟨a, b⟩
  have ha := (List.all_eq_true.mp sum_checked) a (List.mem_finRange a)
  exact of_decide_eq_true ((List.all_eq_true.mp ha) b (List.mem_finRange b))""",
        """private theorem bound_checked :
    (List.finRange 5).all (fun d => decide (machineBound d = bound d)) = true := by cbv""",
        """theorem bound_eq (d : Budget) : machineBound d = bound d := by
  exact of_decide_eq_true ((List.all_eq_true.mp bound_checked) d (List.mem_finRange d))""",
        "end ARMReplay",
    ])
    return "\n".join(declarations) + "\n"


def serve(stage, work, timeout, profile):
    server = FastMCP("arm")
    result_file = work / "replay-result.json"
    stage_cache = stage / "replay-cache.json"

    @server.tool()
    def replay() -> dict:
        """Replay the pinned ARM64 sum and bound functions on every allowed input.

        Returns their tables and the kernel-checked Lean equalities available to
        your final proof. This tool does not check the sensitivity specification.
        """
        started = time.time()
        recorded = result_file.is_file()
        existing = result_file if recorded else stage_cache
        cached = existing.is_file()
        result = json.loads(existing.read_text()) if cached else {}
        try:
            if not cached:
                put(stage / "ReplayValues.lean", DATA)
                values = check_lean(stage, "ReplayValues.lean", timeout=45)
                result["evaluation_seconds"] = values.seconds
                if not values.ok:
                    raise ValueError(f"ARM replay evaluation failed: {values.diagnostics[-1000:]}")
                sums, bounds = (json.loads(line) for line in values.diagnostics.splitlines() if line.strip())
                put(stage / "ReplayFacts.lean", facts_source(sums, bounds))
                certificates = check_lean(
                    stage, "ReplayFacts.lean", output="ReplayFacts.olean", timeout=timeout, profile=profile,
                )
                result["certificate_seconds"] = certificates.seconds
                if not certificates.ok:
                    raise ValueError(f"ARM replay certificates failed: {certificates.diagnostics[-1400:]}")
                result["certificate_sha256"] = digest(stage / "ReplayFacts.lean")
                result["response"] = {"sum": sums, "bound": bounds, "lean_api": API}
                result["status"] = "checked"
                put(stage_cache, json.dumps(result, indent=2) + "\n")
            if result["status"] != "checked":
                raise ValueError(result["error"])
            return result["response"]
        except (ValueError, OSError) as error:
            result.update(status="failed", error=str(error))
            raise
        finally:
            if not recorded:
                for name in ("ReplayValues.lean", "ReplayValues.lean.log",
                             "ReplayFacts.lean", "ReplayFacts.lean.log"):
                    if (stage / name).is_file():
                        shutil.copyfile(stage / name, work / name)
                put(result_file, json.dumps(result | {"cached": cached}, indent=2) + "\n")
            with (work / "replay-calls.jsonl").open("a", encoding="utf-8") as trace:
                trace.write(json.dumps({"tool": "replay", "arguments": {}, "started_unix": started,
                                        "elapsed_seconds": round(time.time() - started, 2),
                                        **result, "cached": cached}) + "\n")

    server.run(transport="stdio")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", type=Path)
    parser.add_argument("work", type=Path)
    parser.add_argument("timeout", type=int)
    parser.add_argument("--profile", action="store_true")
    args = parser.parse_args()
    serve(args.stage, args.work, args.timeout, args.profile)
