"""Trajectory invariant assertions.

Each assertion takes a Trajectory and returns an AssertionResult. These are
the safety/correctness rules you want enforced on every agent run in CI --
e.g. "the payments tool must never fire unless refund eligibility was
checked first" or "the agent must never call execute_sql, period."
"""
from __future__ import annotations

from typing import List, Sequence

from trajence.core.models import AssertionResult, Trajectory


class ToolCalledAssertion:
    """Fails if `tool_name` was never called (optionally: fewer than `min_times`)."""

    def __init__(self, tool_name: str, min_times: int = 1):
        self.tool_name = tool_name
        self.min_times = min_times

    def evaluate(self, trajectory: Trajectory) -> AssertionResult:
        count = trajectory.tool_call_names().count(self.tool_name)
        passed = count >= self.min_times
        return AssertionResult(
            assertion="ToolCalled",
            passed=passed,
            message=(
                f"'{self.tool_name}' called {count} time(s) (>= {self.min_times} required)"
                if passed
                else f"'{self.tool_name}' called only {count} time(s), expected >= {self.min_times}"
            ),
        )


class ToolNeverCalledAssertion:
    """Safety rail: fails if a dangerous/forbidden tool was called at all."""

    def __init__(self, tool_name: str):
        self.tool_name = tool_name

    def evaluate(self, trajectory: Trajectory) -> AssertionResult:
        count = trajectory.tool_call_names().count(self.tool_name)
        passed = count == 0
        return AssertionResult(
            assertion="ToolNeverCalled",
            passed=passed,
            message=(
                f"Safety OK: '{self.tool_name}' was never called"
                if passed
                else f"CRITICAL SAFETY VIOLATION: '{self.tool_name}' was called {count} time(s)"
            ),
        )


class ToolOrderAssertion:
    """Fails unless the given tool names appear as a subsequence, in order.

    (Other tool calls may happen in between -- this checks relative order,
    not that these are the *only* calls.)
    """

    def __init__(self, expected_order: Sequence[str]):
        self.expected_order = list(expected_order)

    def evaluate(self, trajectory: Trajectory) -> AssertionResult:
        actual = trajectory.tool_call_names()
        idx = 0
        for name in actual:
            if idx < len(self.expected_order) and name == self.expected_order[idx]:
                idx += 1
        passed = idx == len(self.expected_order)
        return AssertionResult(
            assertion="ToolOrder",
            passed=passed,
            message=(
                f"Tool order satisfied: {self.expected_order}"
                if passed
                else f"Tool order violated: expected subsequence {self.expected_order}, got {actual}"
            ),
        )


class MaxStepsAssertion:
    """Fails if the agent took more than `max_steps` steps (catches runaway loops)."""

    def __init__(self, max_steps: int):
        self.max_steps = max_steps

    def evaluate(self, trajectory: Trajectory) -> AssertionResult:
        actual = len(trajectory.steps)
        passed = actual <= self.max_steps
        return AssertionResult(
            assertion="MaxSteps",
            passed=passed,
            message=(
                f"{actual} steps (<= {self.max_steps} limit)"
                if passed
                else f"Runaway risk: {actual} steps exceeds limit of {self.max_steps}"
            ),
        )


class BudgetAssertion:
    """Fails if total cost of the run exceeds `max_usd`."""

    def __init__(self, max_usd: float):
        self.max_usd = max_usd

    def evaluate(self, trajectory: Trajectory) -> AssertionResult:
        actual = trajectory.total_cost_usd
        passed = actual <= self.max_usd
        return AssertionResult(
            assertion="Budget",
            passed=passed,
            message=(
                f"${actual:.4f} spent (<= ${self.max_usd:.4f} budget)"
                if passed
                else f"Budget exceeded: ${actual:.4f} > ${self.max_usd:.4f}"
            ),
        )


class NoLoopAssertion:
    """Fails if the same tool call (name + args) repeats more than `max_repeats` times
    consecutively -- a cheap heuristic for detecting an agent stuck in a loop."""

    def __init__(self, max_repeats: int = 3):
        self.max_repeats = max_repeats

    def evaluate(self, trajectory: Trajectory) -> AssertionResult:
        signatures: List[str] = []
        for step in trajectory.steps:
            for tc in step.tool_calls:
                signatures.append(f"{tc.name}:{sorted(tc.arguments.items())}")

        run_len = 1
        max_run = 1
        for i in range(1, len(signatures)):
            if signatures[i] == signatures[i - 1]:
                run_len += 1
                max_run = max(max_run, run_len)
            else:
                run_len = 1

        passed = max_run <= self.max_repeats
        return AssertionResult(
            assertion="NoLoop",
            passed=passed,
            message=(
                f"No repeated-call loop detected (max run: {max_run})"
                if passed
                else f"Loop detected: same tool call repeated {max_run} times consecutively"
            ),
        )
