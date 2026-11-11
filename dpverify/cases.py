"""Load checked-in case files and prepare one opaque binary candidate."""

from dataclasses import dataclass
import json
from pathlib import Path
import re
import shutil
from typing import TypedDict

from .lean import check_lean, put, require_lean
from .toolchain import LEAN_VERSION, MODEL_REVISION, digest

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "cases"
DEFAULT_CASE = "opendp-bounded-sum"


class Provenance(TypedDict):
    lean: str
    rust: str
    arm_model_git: str
    opendp_git: dict[str, str]
    binary_sha256: dict[str, str]
    candidate_order: list[str]
    fixture_sha256: dict[str, str]
    claim: list[str]


@dataclass(frozen=True)
class Candidate:
    directory: Path
    hints: str
    assembly: str


@dataclass(frozen=True)
class Case:
    directory: Path
    provenance: Provenance

    @classmethod
    def load(cls, name: str) -> "Case":
        directory = CASES / name
        provenance = json.loads((directory / "provenance.json").read_text(encoding="utf-8"))
        if (provenance["lean"], provenance["arm_model_git"]) != (LEAN_VERSION, MODEL_REVISION):
            raise ValueError("The case requires a different Lean or ARM64 model version.")
        if (len(provenance["candidate_order"]) != 2
                or set(provenance["candidate_order"]) != set(provenance["binary_sha256"])):
            raise ValueError("The case must map candidates A and B to its two binary snapshots.")
        for filename, expected in provenance["fixture_sha256"].items():
            if digest(directory / filename) != expected:
                raise ValueError(f"Case file differs from its recorded hash: {filename}")
        return cls(directory, provenance)

    @property
    def name(self) -> str:
        return self.directory.name

    @property
    def target(self) -> str:
        return " ".join(f"_root_.{name}" for name in self.provenance["claim"])

    @property
    def supports_replay(self) -> bool:
        return (self.directory / "proof-replay.prompt").is_file()

    def read(self, name: str) -> str:
        return (self.directory / name).read_text(encoding="utf-8")

    def prepare(self, run: Path, candidate: str, *, include_hints: bool) -> Candidate:
        side = self.provenance["candidate_order"][ord(candidate) - ord("A")]
        checksum = self.provenance["binary_sha256"][side]
        stage = run / candidate
        stage.mkdir()

        extraction = self.read("fixtures/ClosureBytes.lean")
        sections = re.split(r"(?=^def )", extraction, flags=re.M)
        selected = [section for section in sections if section.startswith(f"def {side}_")]
        if not selected:
            raise ValueError(f"No instruction snapshot for candidate {candidate}.")
        put(stage / "ClosureBytes.lean", "".join(selected).replace(f"def {side}_", "def binary_"))
        shutil.copyfile(self.directory / "Machine.lean", stage / "Machine.lean")
        if (self.directory / "ReplayCore.lean").is_file():
            shutil.copyfile(self.directory / "ReplayCore.lean", stage / "ReplayCore.lean")
        for name in ("Inputs.lean", "Spec.lean"):
            shutil.copyfile(run / name, stage / name)
        modules = ["Inputs", "Spec", "ClosureBytes"]
        if (stage / "ReplayCore.lean").is_file():
            modules.append("ReplayCore")
        modules.append("Machine")
        for module in modules:
            require_lean(stage, f"{module}.lean")

        hints = ""
        if include_hints:
            put(stage / "Emulate.lean", self.read("Emulate.lean"))
            result = check_lean(stage, "Emulate.lean", timeout=45)
            if not result.ok:
                raise ValueError(f"ARM replay failed in {stage}\n{result.diagnostics[-1200:]}")
            hints = result.diagnostics

        provenance = {
            "candidate": candidate, "sha256": checksum, "source_git": self.provenance["opendp_git"][side],
            "arm_model_git": self.provenance["arm_model_git"], "rust": self.provenance["rust"],
            "lean": self.provenance["lean"], "closure_bytes_sha256": digest(stage / "ClosureBytes.lean"),
            "machine_sha256": digest(stage / "Machine.lean"),
        }
        put(stage / "binary.json", json.dumps(provenance, indent=2) + "\n")
        # Symbols can reveal the historical label. Keep only instruction lines.
        lines = self.read(f"fixtures/{side}.asm").splitlines()
        assembly = "\n".join(line.split("<", 1)[0].rstrip() for line in lines
                             if re.match(r"^\s*[0-9a-f]+:", line))
        return Candidate(stage, hints, assembly)


def available_cases() -> tuple[str, ...]:
    return tuple(sorted(path.parent.name for path in CASES.glob("*/provenance.json")))
