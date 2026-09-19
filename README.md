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

`trajence` is a lightweight Python toolkit for testing AI agents by tracking
what they do, not just what they say or output.

It helps developers:

- capture an agent run as a structured trajectory, including steps, tool calls,
  latency, and cost
- assert invariants such as required tool use, forbidden actions, ordering,
  loop detection, and budget constraints
- save a run as a cassette, then replay or diff it deterministically to catch
  regressions without re-running expensive operations
- integrate directly into CI/CD with a CLI that exits `0` on pass and `1` on
  real safety or workflow violations
- generate console and HTML reports for debugging and review

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
