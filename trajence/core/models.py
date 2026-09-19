"""Core data models for trajence.

These are the structures that every other module (tracer, assertions,
replay engine, reporter) builds on. Kept dependency-light (pydantic only)
so they're easy to serialize to/from JSON for cassette replay.
"""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    id: str = Field(default_factory=lambda: f"call_{uuid.uuid4().hex[:8]}")
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    call_id: str
    name: str
    output: Any = None
    error: Optional[str] = None
    status: str = "success"  # "success" | "error"


class Step(BaseModel):
    step_number: int
    thought: Optional[str] = None
    tool_calls: List[ToolCall] = Field(default_factory=list)
    tool_results: List[ToolResult] = Field(default_factory=list)
    output: Optional[str] = None
    cost_usd: float = 0.0
    latency_ms: float = 0.0


class Trajectory(BaseModel):
    run_id: str
    agent_name: str
    scenario_name: str = "default"
    steps: List[Step] = Field(default_factory=list)
    final_output: Optional[str] = None
    total_cost_usd: float = 0.0
    total_latency_ms: float = 0.0
    created_at: float = Field(default_factory=time.time)

    def tool_call_names(self) -> List[str]:
        """Flat list of every tool name called, in call order."""
        names: List[str] = []
        for step in self.steps:
            names.extend(tc.name for tc in step.tool_calls)
        return names


class AssertionResult(BaseModel):
    assertion: str
    passed: bool
    message: str
    severity: str = "error"  # "error" | "warning"


class ScenarioResult(BaseModel):
    scenario_name: str
    trajectory: Trajectory
    assertion_results: List[AssertionResult] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.assertion_results if r.severity == "error")


class SuiteResult(BaseModel):
    suite_name: str
    scenario_results: List[ScenarioResult] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.scenario_results)

    @property
    def pass_count(self) -> int:
        return sum(1 for r in self.scenario_results if r.passed)

    @property
    def fail_count(self) -> int:
        return len(self.scenario_results) - self.pass_count
