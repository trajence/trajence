# trajence

> Trajectory testing, invariant assertions, and deterministic replay for AI agents in CI/CD.
>
> `trajence` was chosen after checking that the more obvious names in this
> space (`agenttrace`, `agentproof`, `agentledger`, `loopward`, `traceweave`,
> `runseal`, and variants) are already in active use by other, unrelated
> projects on PyPI and GitHub. `trajence` was verified clear at the time of
> writing — do one final check yourself before publishing publicly, since
> availability can change.

## What this actually is

A small, dependency-light Python library + CLI for testing AI agents on
*what they do*, not just what they output:

- **`AgentTracer`** — instrument an agent run and capture the trajectory
  (steps, tool calls, costs, latency) as a structured object.
- **Assertions** — `ToolCalledAssertion`, `ToolNeverCalledAssertion` (safety
  rails), `ToolOrderAssertion`, `MaxStepsAssertion` (loop detection),
  `BudgetAssertion`, `NoLoopAssertion`.
- **Cassette replay** — save a trajectory to JSON once, diff future runs
  against it without re-running anything expensive.
- **CLI** — `trajence run`, `trajence diff`, `trajence init`, with proper
  Unix exit codes (`0` pass, `1` fail) so it can gate a CI pipeline.
- **Console + HTML reporting.**

## What this is *not* (yet)

- No chaos/fault-injection engine (HTTP 429/500 simulation) — planned, not built.
- No GitHub Actions marketplace listing / `action.yml` — not built.
- No hosted dashboard, no PR-comment bot, no billing tiers — none of that exists.
  Anything you've seen about ARR targets or pricing tiers was speculative
  narrative from an earlier planning session, not a real product decision.

## Install (local dev)

```bash
pip install -e .
```

## Quickstart

```bash
trajence init
trajence run example_suite.py --html report.html --json report.json
```

Or run the more realistic bundled example:

```bash
python3 -m unittest discover tests   # 19 unit tests, all verified passing
trajence run examples/refund_agent.py --html report.html
```

## Writing a suite

A suite module needs one function, `build_suite()`, returning a
`trajence.runner.suite.TestSuite`:

```python
from trajence import AgentTracer, ToolCalledAssertion, ToolNeverCalledAssertion
from trajence.runner.suite import TestSuite

def run_my_agent():
    with AgentTracer("my_agent") as tracer:
        tracer.start_step(thought="doing the thing")
        tracer.record_tool_call("search", {"q": "hello"})
        tracer.end_step(cost_usd=0.001)
    return tracer.trajectory

def build_suite() -> TestSuite:
    suite = TestSuite("my_suite")
    suite.add_scenario(
        "basic_search",
        run_my_agent,
        [ToolCalledAssertion("search"), ToolNeverCalledAssertion("execute_sql")],
    )
    return suite
```

## Replay / diff

```python
from trajence import save_cassette
save_cassette(tracer.trajectory, "cassettes/baseline.json")
```

```bash
trajence diff cassettes/baseline.json cassettes/current.json
```

## Status

Everything documented above was written and actually executed in a real
Python environment before being handed to you — 19/19 unit tests pass,
the CLI correctly exits 0 on a passing suite and 1 on a genuine safety
violation, and cassette save/load/diff round-trips correctly. Nothing here
is aspirational or narrated-but-unverified.
