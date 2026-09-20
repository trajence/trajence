# Contributing to Trajence

Thank you for your interest in contributing to Trajence.

Trajence is a small, focused project designed to make AI-agent behavior easier to test, debug, and validate. We welcome contributions that improve the core library, documentation, examples, or developer experience.

## Getting started

### Prerequisites

- Python 3.x
- a working virtual environment
- Git installed locally

### Local setup

```bash
git clone https://github.com/trajence/trajence.git
cd trajence
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Running tests

```bash
python3 -m unittest discover tests
```

If you are testing the CLI or examples locally, use the project entrypoints directly.

## Project goals

When contributing, keep these principles in mind:

- keep the project lightweight;
- prioritize deterministic behavior validation;
- prefer clear, simple APIs;
- preserve the focus on traceability and testability;
- avoid adding unnecessary complexity.

## Contribution workflow

1. Open or find an issue describing the change.
2. Create a feature branch.
3. Make the smallest change that addresses the problem.
4. Add or update tests where relevant.
5. Run the relevant test suite.
6. Update docs if behavior or usage changes.
7. Open a pull request with a clear description.

## Good contribution areas

- assertion improvements
- better error reporting
- CLI usability
- documentation and examples
- trajectory diff improvements
- test coverage
- CI/CD integration helpers

## Pull request expectations

Please keep pull requests focused and understandable. Include the following when appropriate:

- what problem the change solves;
- how it was validated;
- any relevant example output or screenshots;
- whether docs were updated.

## Code style

The project is intentionally simple. Prefer clear naming, direct logic, and readable implementations. Keep new functionality aligned with the core purpose of trajectory-based validation.

## Reporting bugs

If you find a bug or unexpected behavior, please include:

- the command used;
- the relevant configuration or scenario;
- the observed output;
- the expected outcome; and
- any trajectory artifact or report generated.

## Feature proposals

Feature proposals should clearly explain:

- the problem being solved;
- why the feature is relevant to Trajence;
- how it fits the project’s goals;
- what trade-offs or constraints are involved.

## Maintainer expectation

This project is intentionally focused. New features should be evaluated against the project’s purpose: deterministic, inspectable, and reliable testing of agent behavior.

## Community values

We aim for a respectful, practical, and constructive contributor experience. Keep feedback actionable and focused on the technical problem.
