"""Instrumentation: records what an agent actually did, step by step."""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional

from trajence.core.models import Step, ToolCall, ToolResult, Trajectory


class AgentTracer:
    """Context-manager / manual API for recording an agent's trajectory.

    Usage:
        with AgentTracer("refund_agent", "auto_approve_under_100") as tracer:
            tracer.start_step(thought="checking order total")
            call_id = tracer.record_tool_call("lookup_order", {"order_id": "123"})
            tracer.record_tool_result(call_id, "lookup_order", {"total": 42.0})
            tracer.end_step(cost_usd=0.001)
        trajectory = tracer.trajectory
    """

    def __init__(self, agent_name: str = "agent", scenario_name: str = "default"):
        self.run_id = f"tr_{uuid.uuid4().hex[:8]}"
        self.trajectory = Trajectory(
            run_id=self.run_id, agent_name=agent_name, scenario_name=scenario_name
        )
        self._current_step: Optional[Step] = None
        self._step_counter = 0
        self._step_start_time: Optional[float] = None

    def __enter__(self) -> "AgentTracer":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._current_step is not None:
            self.end_step()
        if exc_type is None:
            self.finish()
        return False  # never suppress exceptions

    def start_step(self, thought: Optional[str] = None) -> Step:
        self._step_counter += 1
        self._current_step = Step(step_number=self._step_counter, thought=thought)
        self._step_start_time = time.monotonic()
        return self._current_step

    def record_tool_call(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> str:
        if self._current_step is None:
            self.start_step()
        tc = ToolCall(name=name, arguments=arguments or {})
        self._current_step.tool_calls.append(tc)
        return tc.id

    def record_tool_result(
        self, call_id: str, name: str, output: Any = None,
        error: Optional[str] = None,
    ) -> None:
        if self._current_step is None:
            raise RuntimeError("record_tool_result called with no active step")
        status = "error" if error else "success"
        self._current_step.tool_results.append(
            ToolResult(call_id=call_id, name=name, output=output, error=error, status=status)
        )

    def end_step(self, output: Optional[str] = None, cost_usd: float = 0.0) -> None:
        if self._current_step is None:
            return
        latency_ms = 0.0
        if self._step_start_time is not None:
            latency_ms = (time.monotonic() - self._step_start_time) * 1000
        self._current_step.output = output
        self._current_step.cost_usd = cost_usd
        self._current_step.latency_ms = latency_ms
        self.trajectory.steps.append(self._current_step)
        self._current_step = None
        self._step_start_time = None

    def finish(self, final_output: Optional[str] = None) -> Trajectory:
        if self._current_step is not None:
            self.end_step()
        if final_output is not None:
            self.trajectory.final_output = final_output
        self.trajectory.total_cost_usd = sum(s.cost_usd for s in self.trajectory.steps)
        self.trajectory.total_latency_ms = sum(s.latency_ms for s in self.trajectory.steps)
        return self.trajectory
