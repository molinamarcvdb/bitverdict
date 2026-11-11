# OpenDP bounded sum on ARM64

This reproduces the integer truncation bug in the fixed-size bounded sum. OpenDP shipped the fix in v0.4.0. The two Rust builds use the exact parent and fix commits. [OpenDP changelog](https://github.com/opendp/opendp/blob/v0.4.0/CHANGELOG.md) · [Fix commit](https://github.com/opendp/opendp/commit/a64feeeb31de22ae9b4bdb20097d437cf93e044e)

| Build | OpenDP commit | Advertised bound at input distance 2 | Violations across 256 ordered pairs at their exact distances |
| --- | --- | ---: | ---: |
| Before | `6a6a6c7afa4be180777e42ab84d4542e4649f4aa` | 2 | 34 |
| After | `a64feeeb31de22ae9b4bdb20097d437cf93e044e` | 3 | 0 |

The witness is `[0, 0]` and `[0, 3]`. One removal and one insertion give symmetric distance 2. Both versions compute sums 0 and 3. The old forward map multiplies the distance by `floor((3 - 0) / 2)`. The fixed forward map multiplies the range by `floor(distance / 2)`.

[Spec.lean](Spec.lean) defines one contract. For every pair of two-record datasets with `i32` values in `[0, 3]` and every distance budget in `0..4`, if the multiset symmetric distance is at most that budget, both sums and the advertised bound must return successfully and the bound must cover the absolute change in sums.

[Check.lean](Check.lean) contains the witness, the refutation of the contract on the old build, and a proof of the contract on the fixed build. It connects the executable results to independent definitions of the mathematical sum and bound. The Lean kernel checked all three theorems in about five minutes on this Mac. The axiom audit reports only Lean’s standard `propext` and `Quot.sound`.

## From Rust to the Lean proof

1. [probe.rs](probe.rs) calls the unmodified historical `make_sized_bounded_sum::<i32>(2, (0, 3))` and exercises the resulting transformation through its native API. It reports the actual closure entry addresses relative to a named symbol, the constructor's captured bound constant, and the compiler's `Vec<i32>` layout.
2. [extract.py](extract.py) resolves those addresses to OpenDP closure symbols in the linked ARM64 Mach-O binaries. It copies the instruction bytes for the sum, the forward map and the called integer cast and multiply routines, preserving relative addresses.
3. [ArmReplay.lean](ArmReplay.lean) loads the instructions and invokes DeepMind's ARM64 model for fetch, decode and execution. It builds the initial register and memory state using the observed Rust ABI and decodes a successful `Result<i32, Error>` from the return slot. The model checks instruction fetch from the loaded bytes and memory permissions. [DeepMind ARM64 model](https://github.com/google-deepmind/code-verification/tree/808b4b7ffef198e6a91f71ed776d641a1c236882/arm64-semantics)

The binary proof starts at the compiled closures. It relies on the native fixture and extractor to connect the historical constructor and Rust ABI to the initial Lean state. Its scope is this size, bounds, integer type and distance range. End-to-end differential privacy also depends on the downstream noise mechanism and its composition.

## Reproduce

On Apple Silicon, use Rust 1.94.1, Xcode's LLVM tools, Python 3, and GMP, MPFR and OpenSSL 3. The build links against local C libraries because the bundled 2021 GMP build fails on modern macOS ARM64. Run the main setup first to install the pinned Lean and ARM64 model. [Toolchain setup](../../../README.md#set-up-and-run-offline)

From the repository root, use the same toolchain cache to build and run both historical probes, extract their bytes, and check the reference proofs.

```sh
OPENDP_PILOT_CACHE="${DPVERIFY_CACHE:-$HOME/Library/Caches/dp-binary-verification}" \
  cases/opendp-bounded-sum/native/run.sh
```

Append `--check-only` to reuse both saved binaries. The script writes `before/native.log`, `after/native.log`, `verification.log`, `ClosureBytes.lean`, and the disassemblies under `cases/opendp-bounded-sum/native/build/`.
