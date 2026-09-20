# Trajence architecture

## Overview

Trajence is built around a simple idea: capture the actual execution of an AI agent, then validate that execution against explicit behavior rules. The system is intentionally lightweight so it can be used in local development, automated tests, and CI/CD pipelines.

## Core conceptual model

The central abstraction is a trajectory.

A trajectory is a structured record of what an agent did while running. It includes the sequence of steps, tool calls, metadata, and any relevant execution details such as cost or latency. A trajectory acts as the source of truth for validation and regression testing.

## Main components

### 1. AgentTracer

`AgentTracer` records an agent run and produces a trajectory. It is the component used when a developer wants to trace behavior during execution.

Typical responsibilities:

- start and end execution steps;
- record tool calls;
- track step metadata such as cost or context;
- produce a structured output for validation and reporting.

### 2. Trajectory model

The trajectory represents the actual execution path. It forms the basis for:

- assertions;
- diffs between runs;
- saved cassettes; and
- reporting.

At a high level, the model is a timeline of behavior rather than just a final message or output.

### 3. Assertion layer

Assertions define the rules that a trajectory must satisfy. Examples include:

- tool called at least once;
- tool never called;
- tool ordering constraints;
- loop detection;
- step count limitations; and
- budget or cost thresholds.

Assertions evaluate over a trajectory and return pass/fail outcomes.

### 4. TestSuite

A `TestSuite` groups scenarios that test different behaviors. Each scenario includes:

- a scenario name;
- a function or workflow to run;
- the set of assertions to evaluate.

This structure allows multiple agent behaviors to be validated in a single test run.

### 5. Cassette storage

A cassette is a serialized, saved representation of a trajectory. It can be used as a stable baseline for future regression checks.

Benefits of cassette storage:

- no need to rerun an expensive workflow every time;
- easier regression comparison;
- reproducible debugging of known-good behavior.

### 6. CLI and reporting

The CLI orchestrates test execution, assertion checks, cassette comparison, and reporting. It provides a lightweight path for integration with CI/CD and automated validation.

Reporting surfaces the outcome of a suite in human-readable form for debugging and analysis.

## Data flow

The typical flow looks like this:

1. A developer runs an agent or workflow.
2. `AgentTracer` records the execution as a trajectory.
3. A `TestSuite` evaluates the trajectory against behavioral assertions.
4. The CLI returns pass/fail exit codes.
5. A known-good trajectory may be saved as a cassette.
6. Future runs can be diffed against the cassette to detect regressions.

## Why this architecture works

The design keeps the system simple and focused:

- it validates behavior, not just output;
- it is lightweight and dependency-free;
- it is easy to understand and debug;
- it maps cleanly to CI/CD workflows;
- it is suitable for deterministic validation of tool-using agent runs.

## Relationship to other systems

Trajence sits adjacent to agent runtimes and orchestration systems. It does not replace them. Instead, it provides a validation layer that can be plugged into an existing workflow.

In other words:

- the runtime executes the agent;
- Trajence makes the execution testable and auditable.

## Future architectural direction

As the project grows, the architecture may expand to include:

- richer report and diff UX;
- deeper trace metadata and annotations;
- stronger support for multi-agent or multi-tool workflows;
- governance and audit layers for policy enforcement; and
- optional integrations with hosted dashboards or automation systems.

The design should stay focused on clarity, repeatability, and testability while avoiding unnecessary complexity.
