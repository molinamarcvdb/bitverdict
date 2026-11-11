#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

cache="${OPENDP_PILOT_CACHE:-$HOME/Library/Caches/dp-binary-verification}"
before_rev=1460de1cf84a1e1844534a7c2135b480533099f7
after_rev=e564f2484186fccaa586db033f03060199111c60
history="$cache/opendp-history"
mkdir -p "$cache" build fixtures

if [[ ! -d "$history/.git" ]]; then
  git clone --filter=blob:none --no-checkout https://github.com/opendp/opendp.git "$history"
fi

for side in before after; do
  if [[ "$side" == before ]]; then
    rev="$before_rev"
  else
    rev="$after_rev"
  fi
  checkout="$cache/opendp-overflow-$side"
  if [[ ! -e "$checkout/.git" ]]; then
    git -C "$history" worktree add --detach "$checkout" "$rev"
  fi
  test "$(git -C "$checkout" rev-parse HEAD)" = "$rev"
  git -C "$checkout" diff --exit-code HEAD
  dir="build/$side"
  mkdir -p "$dir"
  ln -sfn "$checkout/rust/opendp" "$dir/opendp"
  cp Cargo.lock "$dir/Cargo.lock"
  cat > "$dir/Cargo.toml" <<'EOF'
[package]
name = "opendp-sum-probe"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "opendp-sum-probe"
path = "../../probe.rs"

[dependencies]
opendp = { path = "opendp", default-features = false }

[features]
historical_bug = []

[profile.release]
debug = "line-tables-only"
panic = "abort"
codegen-units = 1
EOF
  target="$cache/opendp-overflow-target-$side"
  if [[ "$side" == before ]]; then
    CARGO_TARGET_DIR="$target" cargo rustc --locked -j 4 --manifest-path "$dir/Cargo.toml" \
      --release --features historical_bug -- --emit=obj,link 2>&1 | tee "$dir/native-build.log"
  else
    CARGO_TARGET_DIR="$target" cargo rustc --locked -j 4 --manifest-path "$dir/Cargo.toml" \
      --release -- --emit=obj,link 2>&1 | tee "$dir/native-build.log"
  fi
  cp "$target/release/opendp-sum-probe" "$dir/opendp-sum-probe"
  "$dir/opendp-sum-probe" | tee "$dir/native.log"
done

python3 extract.py build/before/opendp-sum-probe build/after/opendp-sum-probe > ../fixtures/ClosureBytes.lean
shasum -a 256 build/{before,after}/opendp-sum-probe ../fixtures/ClosureBytes.lean \
  ../fixtures/{before,after}.asm > build/sha256.txt
