"""Offline end-to-end check using the real SDK and previously verified proof fixtures."""

from argparse import ArgumentParser
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading

from dpverify.cases import CASES, DEFAULT_CASE, ROOT
from dpverify.toolchain import digest


def fixtures():
    native = CASES / DEFAULT_CASE / "native"
    spec = (native / "Spec.lean").read_text()
    spec = "\n".join(line for line in spec.splitlines() if not line.startswith(("--", "abbrev")))
    checked = (native / "Check.lean").read_text()
    fixed = checked[checked.index("theorem fixed_sum_matches"):checked.index("def witnessLeft")]
    fixed = (fixed.replace("newSum", "machineSum").replace("newBound", "machineBound")
             .replace("fixed_satisfies_sensitivity", "candidate"))
    old = checked[checked.index("def witnessLeft"):checked.index("#print axioms")]
    old = (old.replace("oldSum", "machineSum").replace("oldBound", "machineBound")
           .replace("old_violates_sensitivity", "candidate"))
    return spec, fixed, old


@contextmanager
def provider():
    spec, fixed, old = fixtures()
    observed = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            assert self.path == "/v1/chat/completions", self.path
            assert self.headers["Authorization"] == "Bearer smoke-test-key"
            assert not request.get("tools"), request.get("tools")
            observed.append(request)
            prompt = json.dumps(request["messages"])
            if "PUBLIC CONTRACT" in prompt:
                assert "ARM REPLAY HINTS" not in prompt
                answer = spec
            elif "Repair the previous attempt" not in prompt:
                answer = "PROVE\ntheorem candidate : True := True.intro"
            elif re.search(r"some 0, some 0, some 3, some 3, some 6", prompt):
                answer = "PROVE\n" + fixed
            else:
                answer = "REFUTE\n" + old
            base = {"id": "chatcmpl-smoke", "object": "chat.completion.chunk",
                    "created": 1, "model": request["model"]}
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            for chunk in (
                {"choices": [{"index": 0, "delta": {"role": "assistant", "content": answer},
                              "finish_reason": None}]},
                {"choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]},
                {"choices": [], "usage": {"prompt_tokens": 100, "completion_tokens": 75,
                                          "total_tokens": 175}},
            ):
                self.wfile.write(("data: " + json.dumps(base | chunk) + "\n\n").encode())
            self.wfile.write(b"data: [DONE]\n\n")

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}/v1", observed
        finally:
            server.shutdown()
            worker.join()


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", choices=("A", "B"))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    root = args.out.resolve() if args.out else Path(tempfile.mkdtemp(prefix="dp-harness-smoke-")).resolve()
    with provider() as (endpoint, observed):
        command = [sys.executable, "-m", "dpverify", "--endpoint", endpoint, "--fixture-replay"]
        env = os.environ | {"DP_HARNESS_MODEL_KEY": "smoke-test-key"}
        draft = root / "draft"
        proof = root / "proof"
        subprocess.run(command + ["draft", str(draft)], cwd=ROOT, env=env, check=True)
        approve = ["--approve-spec", digest(draft / "Spec.lean"), "--out", str(proof)]
        selection = ["--candidate", args.candidate] if args.candidate else []
        subprocess.run(command + ["verify", str(draft)] + approve + selection, cwd=ROOT, env=env, check=True)
        results = json.loads((proof / "report.json").read_text())
        expected = {"A": "proved", "B": "refuted"}
        assert {r["candidate"]: r["status"] for r in results} == {
            name: expected[name] for name in (args.candidate or "AB")
        }
        assert all(r["attempt"] == 2 for r in results)
        assert json.loads((proof / "experiment.json").read_text())["mode"] == "fixture-replay"
        assert (draft / "spec-1/notifications.jsonl").stat().st_size
        assert json.loads((draft / "spec-1/model.json").read_text())["usage"][0]["totalTokens"] == 175
        assert len(observed) == 1 + 2 * len(results), len(observed)
    print(f"Offline SDK and Lean smoke passed. Evidence is in {root}.")


if __name__ == "__main__":
    main()
