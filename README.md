# Check compiled DP code with Lean

This research pilot asks whether an agent can prove a differential privacy library's sensitivity claim against its compiled code. The first case is a historical integer bounded-sum bug in OpenDP. We check the same claim against the instruction bytes from the buggy and fixed ARM64 builds.

```mermaid
flowchart LR
    Brief["Public contract and input types"] --> Draft["Draft the Lean spec"]
    Draft --> Review["Review and freeze the spec"]
    Binary["Compiled ARM64 functions"] --> Extract["Extract instructions and call layout"]
    Extract --> Machine["DeepMind ARM64 model in Lean"]
    Machine --> Replay["Optional replay tool<br/>Check the function outputs"]
    Review --> Agent["DeepSeek writes a proof or refutation"]
    Machine --> Agent
    Replay --> Agent
    Agent --> Check["Lean checks the claim and audits axioms"]
    Check --> Result["Proved, refuted, or unresolved"]
    Check -. "Diagnostics on retry" .-> Agent
```

The [bounded-sum case](cases/opendp-bounded-sum/README.md) shows an underestimated stability map. The [overflow case](cases/opendp-overflow/README.md) compares the actual compiled sum before and after an integer overflow fix.

The [dataset notes](docs/dataset-sources.md) list other upstream fixes and the work needed to turn them into benchmark cases.

## Try the pilot

Use an Apple Silicon Mac with the Xcode Command Line Tools and [uv](https://docs.astral.sh/uv/). Run these commands from the repo root. The first setup downloads Lean and builds the pinned DeepMind ARM64 model.

```sh
uv sync --locked --python 3.12
uv run --locked python -m dpverify setup
uv run --locked python -m tests.smoke --out runs/offline
```

The smoke check uses a local model fixture. It exercises the same harness and Lean checker and verifies that they accept the fixed proof and the buggy-build refutation. It runs for several minutes. It needs no OpenRouter key.

Setup keeps Lean and the ARM64 model in `~/Library/Caches/dp-binary-verification`. Set `DPVERIFY_CACHE` to use a different directory and keep it set when you run the checker. Setup checks the Lean release archive's SHA-256 and the ARM64 model's Git revision before building.

### Run the agent on OpenRouter

Put `OPENROUTER_API_KEY` in an untracked `.env` file and load it into the terminal.

```sh
set -a
source ./.env
set +a
```

The checked-in [specification](cases/opendp-bounded-sum/Spec.lean) is the reviewed spec from the pilot. This command checks the fixed binary snapshot, candidate A, with the same DeepSeek 1017 model and an automatic retry.

```sh
uv run --locked python -m dpverify --attempts 2 --max-tokens 32768 verify \
  cases/opendp-bounded-sum \
  --approve-spec c9bb4e8cf48219cbd2260a8e23971152e92841debd162154e4cb85a2a07cee36 \
  --candidate A --arm-replay --lean-profile --out runs/fixed
```

Omit `--candidate A` to check both snapshots. Use `--proof-model` after `verify` to try another model. For an OpenAI-compatible vLLM endpoint, pass `--endpoint` before the subcommand, set `DP_HARNESS_MODEL_KEY`, and use the model ID served by vLLM. Use `uv run --locked python -m dpverify draft runs/spec` to draft a new spec, review the resulting `Spec.lean`, and pass its approved hash to `verify`.

### Read the run

- `report.json` lists each candidate's verdict. A timeout or rejected proof yields `unresolved`.
- `experiment.json` records the model, token cap, limits, and file hashes.
- `A/Attempt*.lean` contains the submitted proofs with the harness's fixed wrapper. Adjacent logs contain Lean diagnostics and, with `--lean-profile`, declaration timings.
- `A/proof-*/` preserves prompts, responses, streamed SDK notifications, session events, usage, and replay tool calls.

The replay tool checks tables of machine outputs. DeepSeek writes the theorem that connects those outputs to the sensitivity claim. Lean accepts a verdict only after it checks the theorem and the harness audits its axioms.

## Repository layout

- [dpverify/](dpverify/) contains the workflow, DeepSeek Harness integration, and replay tool.
- [cases/](cases/) contains the frozen specs, extracted instruction snapshots, provenance, and native rebuild recipes for both OpenDP cases.
- [tests/smoke.py](tests/smoke.py) runs the workflow through the real SDK with a local fixture provider.

The check covers the two-record integer contract for the compiled closures and their recorded Rust call layout. It relies on the extractor, call layout, and ARM64 model. The contract does not establish end-to-end privacy for OpenDP or its noise mechanisms.
