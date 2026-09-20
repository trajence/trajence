# trajence

> Deterministic trajectory testing for AI agents.
>
> Capture what an agent does, verify that it follows your rules, and replay its behavior in CI/CD.

`trajence` is a lightweight, dependency-free Python toolkit for testing agent behavior—not just final outputs. It turns an agent run into a structured, inspectable trajectory and gives you tools to validate, compare, and debug that run.

## Why trajence?

Traditional tests usually check an agent's final response. That can miss important parts of an execution: which tools were called, in what order, how many steps were taken, and how much the run cost.

Trajence makes those behaviors testable and repeatable.

## Core capabilities

- **Trace agent runs** — capture steps, tool calls, latency, and cost in a structured trajectory.
- **Assert safety and correctness** — require or forbid tools, enforce tool ordering, detect loops, limit steps, and check budgets.
- **Replay and diff** — save a trajectory as a JSON cassette and compare future runs without repeating expensive work.
- **Run in CI/CD** — use the CLI's standard exit codes (`0` for success, `1` for failure) to gate changes automatically.
- **Generate reports** — inspect results in the console or an HTML report.

## Quickstart

### Install locally

```bash
pip install -e .
```

### Run a suite

```bash
trajence init
trajence run example_suite.py --html report.html --json report.json
```

Run the bundled example and tests:

```bash
python3 -m unittest discover tests
trajence run examples/refund_agent.py --html report.html
```

## Write a suite

A suite module exposes `build_suite()` and returns a `trajence.runner.suite.TestSuite`:

```python
from trajence import (
    AgentTracer,
    ToolCalledAssertion,
    ToolNeverCalledAssertion,
)
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
        [
            ToolCalledAssertion("search"),
            ToolNeverCalledAssertion("execute_sql"),
        ],
    )
    return suite
```

## Save and compare trajectories

Save a known-good run as a cassette:

```python
from trajence import save_cassette

save_cassette(tracer.trajectory, "cassettes/baseline.json")
```

Compare it with a later run:

```bash
trajence diff cassettes/baseline.json cassettes/current.json
```

## Available assertions

The toolkit currently includes assertions for:

- required tool calls
- forbidden tool calls
- tool-call ordering
- maximum step counts
- budget limits
- loop detection

## CI/CD usage

Trajence is designed to run as a normal automated test command. A passing suite exits with `0`; a failed suite exits with `1`, so it can be used directly in a pipeline:

```yaml
- name: Test agent trajectories
  run: |
    pip install -e .
    python3 -m unittest discover tests
    trajence run examples/refund_agent.py --html report.html
```

Store reports and cassette diffs as CI artifacts when investigating a behavior regression.

## Documentation

- [Project brief](PROJECT_BRIEF.md)
- [Roadmap](ROADMAP.md)
- [Architecture](ARCHITECTURE.md)
- [Contributing guide](CONTRIBUTING.md)
- [Usage guide](docs/USAGE.md)
- [Changelog](CHANGELOG.md)

## Current scope

`trajence` currently provides the Python library, CLI, cassette replay and comparison, and console/HTML reporting. Hosted dashboards, pull-request bots, a GitHub Actions marketplace action, and fault-injection features are outside its current scope.

## Project status

The documented workflow has been exercised locally: the test suite reports 19/19 passing tests, the CLI returns the expected pass/fail exit codes, and cassette save/load/diff round-trips successfully.

Trajence is an early-stage project with a working core. The next priorities are broader real-world examples, richer diagnostics, stronger contributor documentation, and validation against more complex agent workflows.

## Core message

> We test how an AI agent behaves, not just what it says.

## License

See the repository license for current licensing terms.
