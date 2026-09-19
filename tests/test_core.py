import tempfile
import unittest
from pathlib import Path

from trajence import AgentTracer
from trajence.core.assertions import (
    BudgetAssertion,
    MaxStepsAssertion,
    NoLoopAssertion,
    ToolCalledAssertion,
    ToolNeverCalledAssertion,
    ToolOrderAssertion,
)
from trajence.core.replay import diff_trajectories, load_cassette, save_cassette
from trajence.runner.suite import TestSuite


def _simple_trajectory():
    with AgentTracer("test_agent", "simple") as tracer:
        tracer.start_step(thought="step 1")
        tracer.record_tool_call("a", {"x": 1})
        tracer.end_step(cost_usd=0.01)
        tracer.start_step(thought="step 2")
        tracer.record_tool_call("b", {"y": 2})
        tracer.end_step(cost_usd=0.02)
    return tracer.trajectory


class TestTracer(unittest.TestCase):
    def test_records_steps_and_calls_in_order(self):
        traj = _simple_trajectory()
        self.assertEqual(len(traj.steps), 2)
        self.assertEqual(traj.tool_call_names(), ["a", "b"])

    def test_total_cost_is_summed(self):
        traj = _simple_trajectory()
        self.assertAlmostEqual(traj.total_cost_usd, 0.03, places=6)

    def test_context_manager_autofinishes(self):
        traj = _simple_trajectory()
        # finish() is called automatically on __exit__; total_cost_usd
        # should already be populated without calling finish() manually.
        self.assertGreater(traj.total_cost_usd, 0)


class TestAssertions(unittest.TestCase):
    def setUp(self):
        self.traj = _simple_trajectory()

    def test_tool_called_passes(self):
        result = ToolCalledAssertion("a").evaluate(self.traj)
        self.assertTrue(result.passed)

    def test_tool_called_fails_when_absent(self):
        result = ToolCalledAssertion("z").evaluate(self.traj)
        self.assertFalse(result.passed)

    def test_tool_never_called_passes_when_absent(self):
        result = ToolNeverCalledAssertion("execute_sql").evaluate(self.traj)
        self.assertTrue(result.passed)

    def test_tool_never_called_fails_when_present(self):
        result = ToolNeverCalledAssertion("a").evaluate(self.traj)
        self.assertFalse(result.passed)

    def test_tool_order_passes_for_correct_subsequence(self):
        result = ToolOrderAssertion(["a", "b"]).evaluate(self.traj)
        self.assertTrue(result.passed)

    def test_tool_order_fails_for_wrong_order(self):
        result = ToolOrderAssertion(["b", "a"]).evaluate(self.traj)
        self.assertFalse(result.passed)

    def test_max_steps_passes_under_limit(self):
        result = MaxStepsAssertion(5).evaluate(self.traj)
        self.assertTrue(result.passed)

    def test_max_steps_fails_over_limit(self):
        result = MaxStepsAssertion(1).evaluate(self.traj)
        self.assertFalse(result.passed)

    def test_budget_passes_under_limit(self):
        result = BudgetAssertion(1.0).evaluate(self.traj)
        self.assertTrue(result.passed)

    def test_budget_fails_over_limit(self):
        result = BudgetAssertion(0.01).evaluate(self.traj)
        self.assertFalse(result.passed)

    def test_no_loop_passes_for_non_repeating_calls(self):
        result = NoLoopAssertion(max_repeats=2).evaluate(self.traj)
        self.assertTrue(result.passed)

    def test_no_loop_fails_for_repeated_identical_calls(self):
        with AgentTracer("looping_agent") as tracer:
            for _ in range(5):
                tracer.start_step()
                tracer.record_tool_call("search", {"q": "same"})
                tracer.end_step()
        result = NoLoopAssertion(max_repeats=3).evaluate(tracer.trajectory)
        self.assertFalse(result.passed)


class TestReplay(unittest.TestCase):
    def test_save_and_load_roundtrip(self):
        traj = _simple_trajectory()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "cassette.json"
            save_cassette(traj, path)
            loaded = load_cassette(path)
        self.assertEqual(loaded.tool_call_names(), traj.tool_call_names())
        self.assertAlmostEqual(loaded.total_cost_usd, traj.total_cost_usd, places=6)

    def test_diff_identical_trajectories_match(self):
        traj = _simple_trajectory()
        diff = diff_trajectories(traj, traj)
        self.assertTrue(diff["equivalent"])
        self.assertEqual(diff["cost_delta_usd"], 0.0)

    def test_diff_detects_divergence(self):
        baseline = _simple_trajectory()
        with AgentTracer("test_agent", "simple") as tracer:
            tracer.start_step()
            tracer.record_tool_call("a", {"x": 1})
            tracer.end_step(cost_usd=0.01)
            tracer.start_step()
            tracer.record_tool_call("execute_sql", {"query": "DROP TABLE users"})
            tracer.end_step(cost_usd=0.02)
        current = tracer.trajectory

        diff = diff_trajectories(baseline, current)
        self.assertFalse(diff["equivalent"])
        self.assertEqual(diff["divergence_index"], 1)


class TestSuiteRunner(unittest.TestCase):
    def test_suite_runs_and_aggregates_pass_fail(self):
        suite = TestSuite("mixed")
        suite.add_scenario(
            "passing", _simple_trajectory, [ToolCalledAssertion("a")]
        )
        suite.add_scenario(
            "failing", _simple_trajectory, [ToolCalledAssertion("nonexistent")]
        )
        result = suite.run()
        self.assertEqual(result.pass_count, 1)
        self.assertEqual(result.fail_count, 1)
        self.assertFalse(result.passed)


if __name__ == "__main__":
    unittest.main()
