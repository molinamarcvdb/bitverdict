"""Install and locate the pinned Lean compiler and DeepMind ARM64 model."""

from dataclasses import dataclass
from hashlib import file_digest
import os
from pathlib import Path
import platform
import subprocess
from tempfile import TemporaryDirectory


LEAN_VERSION = "4.34.0"
LEAN_RELEASE = f"lean-{LEAN_VERSION}-darwin_aarch64"
LEAN_SHA256 = "69f263fa6e21bbc2466bbfb1affcd92479ee2714c883a07de548e099a5922932"
MODEL_REPOSITORY = "https://github.com/google-deepmind/code-verification.git"
MODEL_REVISION = "808b4b7ffef198e6a91f71ed776d641a1c236882"
SEMANTICS_MODULE = "Arm64.Trusted.ISA.Semantics"


def digest(path: Path) -> str:
    with path.open("rb") as source:
        return file_digest(source, "sha256").hexdigest()


def run(*args: str | Path, cwd: Path | None = None) -> None:
    subprocess.run(args, cwd=cwd, check=True)


@dataclass(frozen=True)
class Toolchain:
    cache: Path

    @classmethod
    def from_environment(cls) -> "Toolchain":
        default = Path.home() / "Library/Caches/dp-binary-verification"
        return cls(Path(os.environ.get("DPVERIFY_CACHE", default)).expanduser().resolve())

    @property
    def lean_home(self) -> Path:
        return self.cache / LEAN_RELEASE

    @property
    def lean(self) -> Path:
        return self.lean_home / "bin/lean"

    @property
    def model(self) -> Path:
        return self.cache / "code-verification"

    @property
    def model_package(self) -> Path:
        return self.model / "arm64-semantics/Arm64"

    @property
    def model_library(self) -> Path:
        return self.model_package / ".lake/build/lib/lean"

    def _verify_sources(self) -> None:
        version = subprocess.check_output([self.lean, "--short-version"], text=True).strip()
        revision = subprocess.check_output(["git", "-C", self.model, "rev-parse", "HEAD"],
                                           text=True).strip()
        changes = subprocess.check_output(
            ["git", "-C", self.model, "status", "--porcelain", "--", "arm64-semantics"],
            text=True,
        )
        if version != LEAN_VERSION or revision != MODEL_REVISION or changes:
            raise ValueError(f"Lean or the ARM64 model differs from the pinned version in {self.cache}.")

    def require(self) -> None:
        semantics = self.model_library / "Arm64/Trusted/ISA/Semantics.olean"
        if not self.lean.is_file() or not semantics.is_file():
            raise ValueError(f"Toolchain missing from {self.cache}. Run uv run python -m dpverify setup.")
        self._verify_sources()

    def install(self) -> None:
        if platform.system() != "Darwin" or platform.machine() != "arm64":
            raise ValueError("Setup requires macOS on Apple Silicon.")
        self.cache.mkdir(parents=True, exist_ok=True)
        if not self.lean_home.exists():
            with TemporaryDirectory(prefix="lean-install-", dir=self.cache) as temporary:
                directory = Path(temporary)
                archive = directory / f"{LEAN_RELEASE}.tar.zst"
                release_url = f"https://github.com/leanprover/lean4/releases/download/v{LEAN_VERSION}"
                print(f"Downloading Lean {LEAN_VERSION}.", flush=True)
                run("curl", "--fail", "--location", "--silent", "--show-error", "--retry", "2",
                    "--output", archive, f"{release_url}/{archive.name}")
                if digest(archive) != LEAN_SHA256:
                    raise ValueError("Lean download did not match the pinned SHA-256.")
                run("tar", "-xf", archive, "-C", directory)
                (directory / LEAN_RELEASE).rename(self.lean_home)
        if not self.model.exists():
            with TemporaryDirectory(prefix="arm-install-", dir=self.cache) as temporary:
                checkout = Path(temporary) / "code-verification"
                print("Fetching the pinned ARM64 model.", flush=True)
                run("git", "init", "--quiet", checkout)
                run("git", "fetch", "--quiet", "--depth=1", MODEL_REPOSITORY, MODEL_REVISION,
                    cwd=checkout)
                run("git", "checkout", "--quiet", "--detach", "FETCH_HEAD", cwd=checkout)
                checkout.rename(self.model)
        self._verify_sources()
        run(self.lean_home / "bin/lake", "-d", self.model_package, "build", f"+{SEMANTICS_MODULE}")
        self.require()
        print(f"Lean and the ARM64 model are ready in {self.cache}.")
