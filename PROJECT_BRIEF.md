# Trajence project brief

## Executive summary

Trajence is a lightweight, dependency-free Python toolkit for deterministic testing of AI-agent behavior. It validates the execution path of an agent—not only its final response—by capturing a structured trajectory of steps, tool calls, ordering, cost, and related runtime metadata.

The project gives engineering teams a practical way to define behavioral rules, detect regressions, replay known-good runs, and place agent validation inside CI/CD pipelines.

## Problem

A final answer can look correct even when the agent behaved incorrectly. Traditional output-focused tests may not reveal that an agent:

- called a forbidden tool;
- skipped a required step;
- used tools in the wrong order;
- exceeded a step or cost budget;
- entered a retry or execution loop; or
- changed behavior after a model, prompt, or tool update.

Agent systems need tests for the path they take, not just the answer they return.

## Product promise

> Trajence tests how an AI agent behaves, not just what it says.

A runtime executes the agent; Trajence verifies what the agent actually did.

## Core capabilities

### Trajectory capture

`AgentTracer` records an agent run as a structured, inspectable trajectory. A trajectory can include steps, tool calls, timing, cost, and other execution metadata.

### Behavioral assertions

Suites can enforce rules including:

- required tool calls;
- forbidden tool calls;
- tool-call ordering;
- maximum step counts;
- budget limits; and
- loop detection.

### Cassette replay and comparison

Known-good trajectories can be saved as JSON cassettes and compared with later runs. This supports regression testing without repeatedly incurring the cost of a full agent execution.

### CI/CD integration

The CLI uses conventional exit codes: `0` for success and `1` for failure. This makes trajectory suites suitable for automated quality gates and release pipelines.

### Human-readable reporting

Results can be inspected in the console or exported as HTML for debugging and review.

## Target users

Trajence is intended for:

- AI and LLM application engineers;
- teams building tool-using or autonomous agents;
- platform teams responsible for agent quality and safety;
- developers maintaining internal assistants; and
- teams that need reproducible behavior checks before deployment.

## Example use cases

1. **Safety validation** — ensure an agent never invokes a restricted tool.
2. **Workflow validation** — require a lookup or approval step before an action.
3. **Regression testing** — compare a new run with a known-good baseline.
4. **Cost control** — enforce step, latency, or budget limits.
5. **Debugging** — inspect the exact point where an execution diverged.
6. **Release gating** — block changes that violate agent behavior rules.

## Technical model

The core workflow is intentionally simple:

1. Run an agent inside `AgentTracer`.
2. Capture the resulting trajectory.
3. Add the trajectory to a `TestSuite` scenario.
4. Evaluate assertions against the run.
5. Report results through the CLI or HTML output.
6. Save and compare cassettes when a stable baseline is useful.

This keeps the framework independent of a particular model provider or agent runtime. Trajence is a validation layer that can sit around an existing implementation.

## Current state

The repository is early-stage but has a functioning core workflow. The documented local validation includes:

- 19/19 passing tests;
- expected CLI pass/fail exit codes; and
- successful cassette save/load/diff round-trips.

Current scope includes the Python library, CLI, tracing, assertions, cassette comparison, and console/HTML reporting.

## Near-term priorities

- Add realistic examples covering multi-step, retry, and tool-heavy agents.
- Improve failure messages and trajectory diff readability.
- Document assertion semantics and CLI behavior in greater depth.
- Add contributor setup, testing, and release guidance.
- Validate the toolkit against a broader set of real-world workflows.
- Establish a changelog and a clear versioning/release process.

## Future direction

Potential future extensions include hosted dashboards, pull-request integrations, a GitHub Actions distribution, and fault-injection capabilities. These are intentionally outside the current scope so the core library can remain focused, lightweight, and dependable.

## Success criteria

Trajence will be successful when teams can confidently answer these questions before deployment:

- Did the agent use only the tools it was allowed to use?
- Did it follow the required workflow?
- Did it stay within its step and cost budgets?
- Did its behavior regress after a code or model change?
- Can an engineer quickly understand and reproduce a failure?
