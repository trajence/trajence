"""Cassette recording + diffing.

Save a Trajectory as a JSON "cassette" once. Later, compare a fresh
trajectory against that baseline without needing to re-run any real
(costly) LLM calls -- this is what makes CI runs cheap and fast.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from trajence.core.models import CURRENT_SCHEMA_VERSION, Trajectory


def save_cassette(trajectory: Trajectory, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(trajectory.model_dump_json(indent=2))


def load_cassette(path: str | Path) -> Trajectory:
    path = Path(path)
    data = json.loads(path.read_text())

    file_version = data.get("schema_version", 0)  # 0 = cassette predates this field
    if file_version > CURRENT_SCHEMA_VERSION:
        raise ValueError(
            f"Cassette at {path} was saved with trajence schema v{file_version}, "
            f"but this installed version only supports up to v{CURRENT_SCHEMA_VERSION}. "
            "Upgrade trajence to load it."
        )
    if file_version < CURRENT_SCHEMA_VERSION:
        data = _migrate_cassette(data, from_version=file_version)

    return Trajectory.model_validate(data)


def _migrate_cassette(data: Dict[str, Any], from_version: int) -> Dict[str, Any]:
    """Upgrade an older cassette's raw dict to the current schema version.

    Add one `if from_version < N: ...transform...` block per future schema
    bump. There's nothing to transform yet -- v1 is the first versioned
    schema -- this just stamps the field so future changes have a place
    to hook in without breaking old cassettes silently.
    """
    data = dict(data)
    data["schema_version"] = CURRENT_SCHEMA_VERSION
    return data


def diff_trajectories(baseline: Trajectory, current: Trajectory) -> Dict[str, Any]:
    """Structural diff between two trajectories: tool-call sequence and cost drift.

    Returns a dict rather than raising, so callers (CLI, reporter) decide
    what to do with a mismatch.
    """
    baseline_calls = baseline.tool_call_names()
    current_calls = current.tool_call_names()

    tool_sequence_match = baseline_calls == current_calls
    step_count_delta = len(current.steps) - len(baseline.steps)
    cost_delta_usd = current.total_cost_usd - baseline.total_cost_usd

    divergence_index = None
    if not tool_sequence_match:
        for i, (a, b) in enumerate(zip(baseline_calls, current_calls)):
            if a != b:
                divergence_index = i
                break
        else:
            divergence_index = min(len(baseline_calls), len(current_calls))

    return {
        "tool_sequence_match": tool_sequence_match,
        "baseline_tool_calls": baseline_calls,
        "current_tool_calls": current_calls,
        "divergence_index": divergence_index,
        "step_count_delta": step_count_delta,
        "cost_delta_usd": round(cost_delta_usd, 6),
        "equivalent": tool_sequence_match,
    }
