"""Runs a set of named scenarios (each producing a Trajectory) against a
list of assertions, and rolls the results up into a SuiteResult."""
from __future__ import annotations

from typing import Callable, Dict, List

from trajence.core.models import ScenarioResult, SuiteResult, Trajectory

Scenario = Callable[[], Trajectory]


class TestSuite:
    def __init__(self, name: str):
        self.name = name
        self._scenarios: Dict[str, Scenario] = {}
        self._assertions: Dict[str, List] = {}

    def add_scenario(self, name: str, run_fn: Scenario, assertions: List) -> None:
        self._scenarios[name] = run_fn
        self._assertions[name] = assertions

    def run(self) -> SuiteResult:
        scenario_results: List[ScenarioResult] = []
        for name, run_fn in self._scenarios.items():
            trajectory: Trajectory = run_fn()
            assertion_results = [a.evaluate(trajectory) for a in self._assertions[name]]
            scenario_results.append(
                ScenarioResult(
                    scenario_name=name,
                    trajectory=trajectory,
                    assertion_results=assertion_results,
                )
            )
        return SuiteResult(suite_name=self.name, scenario_results=scenario_results)
