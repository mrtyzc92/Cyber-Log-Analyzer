from cyber_log_analyzer.agents.decisions import AgentAction, AgentDecision
from cyber_log_analyzer.agents.evals import (
    DecisionEvalCase,
    evaluate_decision_maker,
)
from cyber_log_analyzer.agents.state import AgentState


class GoalBasedDecisionMaker:
    def decide(self, state: AgentState) -> AgentDecision:
        if "analyze" in state.goal.lower():
            return AgentDecision(
                action=AgentAction.USE_TOOL,
                reason="The log requires analysis",
                tool_name="log_analyzer",
                tool_input="sample.log",
            )

        return AgentDecision(
            action=AgentAction.COMPLETE,
            reason="No work is required",
        )


def test_evaluate_decision_maker_reports_passing_cases():
    cases = (
        DecisionEvalCase(
            name="analysis uses approved tool",
            goal="Analyze the security log",
            expected_action=AgentAction.USE_TOOL,
            expected_tool_name="log_analyzer",
        ),
        DecisionEvalCase(
            name="finished task completes",
            goal="Report is already finished",
            expected_action=AgentAction.COMPLETE,
        ),
    )

    report = evaluate_decision_maker(GoalBasedDecisionMaker(), cases)

    assert report.total == 2
    assert report.passed == 2
    assert report.accuracy == 1.0
    assert report.failures == ()


def test_evaluate_decision_maker_explains_action_mismatch():
    cases = (
        DecisionEvalCase(
            name="must fail safely",
            goal="Report is already finished",
            expected_action=AgentAction.FAIL,
        ),
    )

    report = evaluate_decision_maker(GoalBasedDecisionMaker(), cases)

    assert report.total == 1
    assert report.passed == 0
    assert report.accuracy == 0.0
    assert report.failures[0].case_name == "must fail safely"
    assert report.failures[0].message == (
        "Expected action fail, received complete"
    )


class CrashingDecisionMaker:
    def decide(self, state: AgentState) -> AgentDecision:
        raise RuntimeError("unexpected provider error")


def test_evaluate_decision_maker_records_runtime_error():
    cases = (
        DecisionEvalCase(
            name="provider outage",
            goal="Analyze the security log",
            expected_action=AgentAction.FAIL,
        ),
    )

    report = evaluate_decision_maker(CrashingDecisionMaker(), cases)

    assert report.passed == 0
    assert report.failures[0].message == (
        "Decision maker raised RuntimeError: unexpected provider error"
    )
