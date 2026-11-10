#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

cache="${OPENDP_PILOT_CACHE:-$HOME/Library/Caches/lean-binary-dp-demo}"
model_rev=808b4b7ffef198e6a91f71ed776d641a1c236882
before_rev=6a6a6c7afa4be180777e42ab84d4542e4649f4aa
after_rev=a64feeeb31de22ae9b4bdb20097d437cf93e044e

if [[ "$#" -gt 1 || "${1:-}" != "" && "${1:-}" != "--check-only" ]]; then
  printf 'Usage: %s [--check-only]\n' "$0" >&2
  exit 1
fi

mkdir -p "$cache" build
model="$cache/code-verification"
if [[ ! -d "$model/.git" ]]; then
  git clone --filter=blob:none https://github.com/google-deepmind/code-verification.git "$model"
  git -C "$model" checkout --detach "$model_rev"
fi
test "$(git -C "$model" rev-parse HEAD)" = "$model_rev"
git -C "$model" diff --exit-code HEAD -- arm64-semantics
arm="$model/arm64-semantics/Arm64"

lean_bin="${LEAN_BIN_DIR:-$cache/lean-4.34.0-darwin_aarch64/bin}"
if [[ -x "$lean_bin/lean" ]]; then
  lean="$lean_bin/lean"
  lake="$lean_bin/lake"
else
  lean=lean
  lake=lake
fi
"$lean" --version | tee build/lean-version.log
grep -q 'version 4\.34\.0,' build/lean-version.log
"$lake" -d "$arm" build +Arm64.Trusted.ISA.Semantics

if [[ "${1:-}" != "--check-only" ]]; then
  rustc --version --verbose | tee build/rust-version.log
  grep -q '^rustc 1\.94\.1 ' build/rust-version.log
  grep -q '^host: aarch64-apple-darwin$' build/rust-version.log

  gmp="${GMP_DIR:-$(brew --prefix gmp)}"
  mpfr="${MPFR_DIR:-$(brew --prefix mpfr)}"
  export OPENSSL_DIR="${OPENSSL_DIR:-$(brew --prefix openssl@3)}"
  export OPENSSL_NO_VENDOR=1
  export C_INCLUDE_PATH="$gmp/include:$mpfr/include"
  export LIBRARY_PATH="$gmp/lib:$mpfr/lib"
  export RUSTFLAGS="-L native=$gmp/lib -L native=$mpfr/lib"

  history="$cache/opendp-history"
  if [[ ! -d "$history/.git" ]]; then
    git clone --filter=blob:none --no-checkout https://github.com/opendp/opendp.git "$history"
  fi

  for side in before after; do
    flags=(--release)
    if [[ "$side" == before ]]; then
      rev="$before_rev"
      flags+=(--features historical_bug)
    else
      rev="$after_rev"
    fi
    checkout="$cache/opendp-$side"
    if [[ ! -e "$checkout/.git" ]]; then
      git -C "$history" worktree add --detach "$checkout" "$rev"
    fi
    test "$(git -C "$checkout" rev-parse HEAD)" = "$rev"
    git -C "$checkout" diff --exit-code HEAD

    dir="build/$side"
    target="$cache/opendp-pilot-target-$side"
    mkdir -p "$dir"
    cp Cargo.lock "$dir/Cargo.lock"
    cat > "$dir/Cargo.toml" <<EOF
[package]
name = "opendp-sum-probe"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "opendp-sum-probe"
path = "../../probe.rs"

[dependencies]
opendp = { path = "$checkout/rust/opendp", features = ["contrib", "use-system-libs"] }

[features]
historical_bug = []

[profile.release]
debug = "line-tables-only"
panic = "abort"
codegen-units = 1
EOF
    CARGO_TARGET_DIR="$target" cargo rustc --locked -j 4 \
      --manifest-path "$dir/Cargo.toml" "${flags[@]}" -- --emit=obj,link \
      2>&1 | tee "$dir/native-build.log"
    cp "$target/release/opendp-sum-probe" "$dir/opendp-sum-probe"
    "$dir/opendp-sum-probe" | tee "$dir/native.log"
  done
fi

python3 extract.py build/before/opendp-sum-probe build/after/opendp-sum-probe > build/ClosureBytes.lean
shasum -a 256 build/{before,after}/opendp-sum-probe build/ClosureBytes.lean > build/sha256.txt

export LEAN_PATH="$arm/.lake/build/lib/lean:$PWD/build"
"$lean" -o build/Spec.olean Spec.lean
"$lean" --root="$PWD" -o build/ClosureBytes.olean build/ClosureBytes.lean
"$lean" -o build/ArmReplay.olean ArmReplay.lean
"$lean" Check.lean 2>&1 | tee build/verification.log
