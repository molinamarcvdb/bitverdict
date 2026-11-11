# Historical DP bug candidates

These revision pairs come from upstream Git history. Each “before” revision is the first parent of the fix. The proposed checks describe what a new fixture would need to establish. A revision pair becomes a benchmark case after both builds and the same frozen claim have been checked.

## Implemented case

### OpenDP unsized bounded-sum overflow

The July 23, 2021 fix changed `make_bounded_sum` from an ordinary integer sum to saturating addition. The stability constant remains the maximum absolute input bound. [Before](https://github.com/opendp/opendp/commit/1460de1cf84a1e1844534a7c2135b480533099f7) · [Fix](https://github.com/opendp/opendp/commit/e564f2484186fccaa586db033f03060199111c60)

The pilot compiled both revisions and checked the sum against the same Lean sensitivity claim. Appending `1` to `[2^30, 2^30 - 1]` changes the old sum from `i32::MAX` to `i32::MIN`. The fixed sum stays at `i32::MAX`. The native probe checks the stability map, and Lean replays the compiled sum using a variable-length Rust input and signed result decoding. [Case and reproduction steps](../cases/opendp-overflow/README.md) · [Run report](../cases/opendp-overflow/evidence/deepseek-v4.1-flash-1017/report.json)

## Native cases that need more modeling

### OpenDP tree aggregation overflow

The October 23, 2026 fix changed internal tree sums to saturating arithmetic, added checked tree sizing, and gave the constructor separate input and output metrics. The regression tests include two-leaf trees at both ends of the `i32` range. [Before](https://github.com/opendp/opendp/commit/bef544460ab8117c5b7071ca7f3aa6df3ea7432e) · [Fix](https://github.com/opendp/opendp/commit/e4b5d025e0af5933bccc8c2c3380597b46f99f5d)

**Proposed check.** For `[i32::MAX, 0]` and `[i32::MAX, 1]`, check that the full tree output changes by at most the advertised L1 bound. Start with the regression's two-leaf layout. The compiled closure allocates and returns a vector.

### Google DP quantile-tree range overflow

The November 28, 2024 fix added constructor checks for a nonfinite floating-point width and a signed integer width that cannot fit its type. The upstream tests exercise `[-1.7e308, 1.7e308]` and the full signed 64-bit range. [Before](https://github.com/google/differential-privacy/commit/0a80e37c1d08feaae798f9ce54cf12c1781a5927) · [Fix](https://github.com/google/differential-privacy/commit/d986e7ffc084ba6924d37b738df31f0638c01fe0)

**Proposed check.** Prove that `QuantileTree::Builder` rejects widths outside the supported range before computing tree indices. The integer example avoids floating-point semantics. This is a constructor safety check. It needs a C++ build and a way to interpret the builder result and allocation calls.

### OpenDP underflow in directed rounding

The September 9, 2024 fix worked around a Dashu conversion that rounded half the smallest positive `f32` to zero under an upward rounding policy. The upstream regression checks conversion to the smallest positive subnormal. [Before](https://github.com/opendp/opendp/commit/660f0cedec169c5d3b25f81fcce036de83cc98a1) · [Fix](https://github.com/opendp/opendp/commit/d000586326c8bb3badb306d8015f491b8d4c3695) · [Upstream report](https://github.com/opendp/opendp/issues/1997)

**Proposed check.** Use the regression value and require the resulting `f32` to be at least the exact positive input. Pin the Dashu dependency as part of the build. Replay needs to account for the arbitrary-precision input representation and conversion calls.

### OpenDP zCDP conversion rounding

The July 30, 2026 fix changed rounding directions in the calculation of `delta`. One upstream regression was previously rounded one unit in the last place lower. Another exercises the subtraction of one from an `alpha` larger than `2^53`. [Before](https://github.com/opendp/opendp/commit/b901ba7b92bb5da9f5b29b8af7476421d1601556) · [Fix](https://github.com/opendp/opendp/commit/2b5d9c5d930520a485920a938f022fe163aca29e)

**Proposed check.** Require a conservative bound at the regression values, using an independently justified reference interval. The code calls logarithm and exponential routines, so their results need explicit models or checked enclosures.

### OpenDP accounting after failed invocations

The November 5, 2026 fix moved accounting ahead of a validated adaptive invocation. Previously an invocation could return an error after fallible postprocessing without recording privacy loss. Upstream tests distinguish this path from a query rejected before invocation. [Before](https://github.com/opendp/opendp/commit/152dcde010221edf24e1743c83eb5ae10b99eca9) · [Fix](https://github.com/opendp/opendp/commit/778ab66cc550a3bbf1cebfcf43b1945e7c6d4f91) · [Upstream report](https://github.com/opendp/opendp/issues/3104)

**Proposed check.** Replay one failing postprocessor and one pre-invocation rejection. Require the former to record the privacy map and the latter to leave the budget unchanged. The real path needs state, callbacks, and error propagation.

## Python cases

### Opacus adaptive-clipping accounting

The March 6, 2026 fix preserves the configured noise multiplier for privacy accounting and applies the adjusted multiplier only when adding gradient noise. Previously the optimizer overwrote the value read by the accountant. [Before](https://github.com/meta-pytorch/opacus/commit/c5a40e6b75693dbf9daea1483b4552447cb7516d) · [Fix](https://github.com/meta-pytorch/opacus/commit/9d3c2b01927e9227ca88095144aee02c9b7bc7fd)

**Proposed check.** Capture the multiplier passed to the accountant during one optimizer step and compare it with the configured value. A deterministic check can record the noise scale passed to the sampler separately. A compiled-code experiment would need a model of the Python and PyTorch execution path.

### SmartNoise covariance clipping

The February 19, 2026 fix changed the covariance calculation to use the clipped data prepared by the function. The regression uses out-of-bound rows and forces zero sampling noise to inspect the input to the mechanism. [Before](https://github.com/opendp/smartnoise-sdk/commit/b4f0058d27eb08b0784864170a1c0bfa875b1c6f) · [Fix](https://github.com/opendp/smartnoise-sdk/commit/5e5fac85e4f1bb5cfd53bb4c5a35470fd995903e)

**Proposed check.** Verify that the deterministic covariance uses clipped values on the upstream regression fixture. Testing the compiled path also requires capturing how Python passes its data into the numerical library. The sampling override belongs in the regression and gives no guarantee about the released noise distribution.
