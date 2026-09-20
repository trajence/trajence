# Trajence usage guide

This guide covers the expected workflow for using Trajence in development and CI/CD.

## Typical workflow

1. Build or run an agent session.
2. Wrap the run in `AgentTracer`.
3. Record tool calls and execution steps.
4. Add the run to a `TestSuite`.
5. Define assertions for safe, expected behavior.
6. Execute the suite via the CLI or test runner.
7. Save known-good trajectories as cassettes.
8. Compare future runs with those baselines.

## Basic example

```python
from trajence import AgentTracer, ToolCalledAssertion, ToolNeverCalledAssertion
from trajence.runner.suite import TestSuite


def run_my_agent():
    with AgentTracer("my_agent") as tracer:
        tracer.start_step(thought="looking up the customer")
        tracer.record_tool_call("search_customer", {"id": "42"})
        tracer.end_step(cost_usd=0.003)
    return tracer.trajectory


def build_suite() -> TestSuite:
    suite = TestSuite("customer_workflow")
    suite.add_scenario(
        "search_then_use",
        run_my_agent,
        [
            ToolCalledAssertion("search_customer"),
            ToolNeverCalledAssertion("delete_customer"),
        ],
    )
    return suite
```

## Running a suite from the CLI

```bash
trajence init
trajence run example_suite.py --html report.html --json report.json
```

The CLI returns standard process exit codes:

- `0` = pass
- `1` = fail

This makes it easy to use Trajence in CI/CD pipelines.

## Saving a baseline cassette

```python
from trajence import save_cassette

save_cassette(tracer.trajectory, "cassettes/baseline.json")
```

## Comparing trajectories

```bash
trajence diff cassettes/baseline.json cassettes/current.json
```

This is particularly useful when you want to check that new runs stay within the accepted behavior envelope.

## Assertions

Common assertions include:

- required tool calls
- forbidden tool calls
- ordering constraints
- loop detection
- step count limits
- budget caps

These assertions let you encode guardrails around real agent behavior rather than only validating final outputs.

## CI/CD use

Typical CI usage looks like this:

```yaml
steps:
  - uses: actions/checkout@v4
  - name: Install
    run: pip install -e .
  - name: Run trajectories
    run: trajence run example_suite.py --html report.html --json report.json
```

If your checks fail, the job exits non-zero and blocks the pipeline.

## Recommended testing pattern

- Use deterministic inputs when possible.
- Keep suites focused on a single workflow.
- Save baseline cassettes for stable behavior.
- Assert against safety, required tools, and ordering constraints.
- Review reports when a trajectory changes unexpectedly.

## Best practices

- Keep assertions specific and explainable.
- Prefer explicit safety requirements over implicit assumptions.
- Capture baselines for known-good workflows.
- Use CI to validate new agent behavior before deployment.
- Treat trajectory diffs as debugging artifacts, not just pass/fail results.
