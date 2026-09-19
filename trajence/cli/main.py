"""trajence CLI.

Commands:
    trajence run <module_path> [--html out.html] [--json out.json]
        Imports `module_path`, calls its `build_suite()` function (must
        return a trajence.runner.suite.TestSuite), runs it, and reports
        results. Exits 1 if any scenario fails (so it blocks CI).

    trajence diff <baseline_cassette.json> <current_cassette.json>
        Compares two saved Trajectory cassettes and reports whether the
        tool-call sequence matches.

    trajence init
        Scaffolds a starter example in the current directory.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

from trajence import __version__
from trajence.core.replay import diff_trajectories, load_cassette
from trajence.runner.reporter import print_console_report, write_html_report, write_json_report
from trajence.runner.suite import TestSuite


def _load_module(path_str: str):
    path = Path(path_str)
    if not path.exists():
        print(f"error: module not found: {path}", file=sys.stderr)
        sys.exit(2)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def cmd_run(args: argparse.Namespace) -> int:
    module = _load_module(args.module)
    if not hasattr(module, "build_suite"):
        print(f"error: {args.module} has no build_suite() function", file=sys.stderr)
        return 2
    suite: TestSuite = module.build_suite()
    result = suite.run()

    print_console_report(result)
    if args.html:
        write_html_report(result, args.html)
        print(f"\nHTML report written to {args.html}")
    if args.json:
        write_json_report(result, args.json)
        print(f"JSON report written to {args.json}")

    return 0 if result.passed else 1


def cmd_diff(args: argparse.Namespace) -> int:
    baseline = load_cassette(args.baseline)
    current = load_cassette(args.current)
    diff = diff_trajectories(baseline, current)

    if diff["equivalent"]:
        print(f"MATCH: trajectories are tool-sequence equivalent "
              f"(cost delta: ${diff['cost_delta_usd']:+.4f})")
        return 0
    else:
        print("MISMATCH: trajectories diverged")
        print(f"  baseline tool calls: {diff['baseline_tool_calls']}")
        print(f"  current  tool calls: {diff['current_tool_calls']}")
        print(f"  diverged at index:   {diff['divergence_index']}")
        print(f"  cost delta:          ${diff['cost_delta_usd']:+.4f}")
        return 1


def cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.path or ".")
    example = target / "example_suite.py"
    if example.exists():
        print(f"error: {example} already exists", file=sys.stderr)
        return 2
    example.write_text(EXAMPLE_SUITE_TEMPLATE)
    print(f"Wrote {example}")
    print(f"Try it: trajence run {example}")
    return 0


EXAMPLE_SUITE_TEMPLATE = '''"""Minimal trajence example: a fake agent, one happy-path scenario,
one safety scenario. Run with: trajence run example_suite.py"""
from trajence import (
    AgentTracer,
    ToolCalledAssertion,
    ToolNeverCalledAssertion,
)
from trajence.runner.suite import TestSuite


def run_happy_path():
    with AgentTracer("demo_agent", "happy_path") as tracer:
        tracer.start_step(thought="looking up the order")
        cid = tracer.record_tool_call("lookup_order", {"order_id": "1"})
        tracer.record_tool_result(cid, "lookup_order", {"total": 42.0})
        tracer.end_step(cost_usd=0.001)
    return tracer.trajectory


def run_forbidden_tool():
    with AgentTracer("demo_agent", "should_never_run_sql") as tracer:
        tracer.start_step(thought="a malicious prompt tries to trigger SQL")
        tracer.record_tool_call("lookup_order", {"order_id": "1"})
        tracer.end_step(cost_usd=0.001)
    return tracer.trajectory


def build_suite() -> TestSuite:
    suite = TestSuite("example_suite")
    suite.add_scenario(
        "happy_path", run_happy_path,
        [ToolCalledAssertion("lookup_order")],
    )
    suite.add_scenario(
        "should_never_run_sql", run_forbidden_tool,
        [ToolNeverCalledAssertion("execute_sql")],
    )
    return suite
'''


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="trajence")
    parser.add_argument("--version", action="version", version=f"trajence {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="run a test suite module")
    p_run.add_argument("module", help="path to a .py file with a build_suite() function")
    p_run.add_argument("--html", help="write an HTML report to this path")
    p_run.add_argument("--json", help="write a JSON report to this path")
    p_run.set_defaults(func=cmd_run)

    p_diff = sub.add_parser("diff", help="diff two saved cassettes")
    p_diff.add_argument("baseline")
    p_diff.add_argument("current")
    p_diff.set_defaults(func=cmd_diff)

    p_init = sub.add_parser("init", help="scaffold an example suite")
    p_init.add_argument("path", nargs="?", default=".")
    p_init.set_defaults(func=cmd_init)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
