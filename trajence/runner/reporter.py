"""Turns a SuiteResult into human-readable output: a colored console
summary, and a self-contained HTML report."""
from __future__ import annotations

import json
from pathlib import Path

from trajence.core.models import SuiteResult

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_console_report(result: SuiteResult) -> None:
    print(f"\n{BOLD}Suite: {result.suite_name}{RESET}")
    print("-" * 60)
    for scenario in result.scenario_results:
        status = f"{GREEN}PASS{RESET}" if scenario.passed else f"{RED}FAIL{RESET}"
        print(f"[{status}] {scenario.scenario_name}")
        for a in scenario.assertion_results:
            mark = f"{GREEN}✓{RESET}" if a.passed else f"{RED}✗{RESET}"
            print(f"    {mark} {a.assertion}: {a.message}")
    print("-" * 60)
    total = len(result.scenario_results)
    print(
        f"{BOLD}{result.pass_count}/{total} scenarios passed{RESET}"
        + ("" if result.passed else f"  {RED}({result.fail_count} failed){RESET}")
    )


def write_json_report(result: SuiteResult, path: str | Path) -> None:
    path = Path(path)
    path.write_text(result.model_dump_json(indent=2))


def write_html_report(result: SuiteResult, path: str | Path) -> None:
    path = Path(path)
    rows = []
    for scenario in result.scenario_results:
        badge_color = "#16a34a" if scenario.passed else "#dc2626"
        badge_text = "PASS" if scenario.passed else "FAIL"
        assertion_rows = "".join(
            f'<li class="{"ok" if a.passed else "bad"}">'
            f'<span class="mark">{"✓" if a.passed else "✗"}</span> '
            f'<strong>{a.assertion}</strong>: {a.message}</li>'
            for a in scenario.assertion_results
        )
        step_rows = "".join(
            f'<li>Step {s.step_number}: {", ".join(tc.name for tc in s.tool_calls) or "(no tool calls)"}'
            f' &mdash; ${s.cost_usd:.4f}</li>'
            for s in scenario.trajectory.steps
        )
        rows.append(f"""
        <details class="scenario">
          <summary>
            <span class="badge" style="background:{badge_color}">{badge_text}</span>
            {scenario.scenario_name}
          </summary>
          <div class="body">
            <h4>Assertions</h4>
            <ul class="assertions">{assertion_rows}</ul>
            <h4>Trajectory ({len(scenario.trajectory.steps)} steps, ${scenario.trajectory.total_cost_usd:.4f})</h4>
            <ul class="steps">{step_rows}</ul>
          </div>
        </details>
        """)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>trajence report — {result.suite_name}</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, sans-serif; max-width: 800px; margin: 40px auto; color: #1a1a1a; }}
  h1 {{ font-size: 1.4rem; }}
  .summary {{ font-weight: 600; margin-bottom: 20px; }}
  .scenario {{ border: 1px solid #e5e5e5; border-radius: 8px; margin-bottom: 10px; padding: 10px 14px; }}
  summary {{ cursor: pointer; font-weight: 600; }}
  .badge {{ color: white; border-radius: 4px; padding: 2px 8px; font-size: 0.75rem; margin-right: 10px; }}
  .body {{ margin-top: 12px; }}
  ul {{ list-style: none; padding-left: 0; }}
  li {{ padding: 3px 0; }}
  .ok .mark {{ color: #16a34a; }}
  .bad .mark {{ color: #dc2626; }}
  .steps li {{ color: #555; font-size: 0.9rem; }}
</style>
</head>
<body>
  <h1>trajence report — {result.suite_name}</h1>
  <div class="summary">{result.pass_count}/{len(result.scenario_results)} scenarios passed</div>
  {"".join(rows)}
</body>
</html>"""
    path.write_text(html)
