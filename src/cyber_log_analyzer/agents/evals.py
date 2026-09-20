from collections.abc import Iterable
from dataclasses import dataclass

from cyber_log_analyzer.agents.decisions import AgentAction
from cyber_log_analyzer.agents.loop import DecisionMaker
from cyber_log_analyzer.agents.state import AgentState


@dataclass(frozen=True)
class DecisionEvalCase:
    """Describe one expected decision behavior."""

    name: str
    goal: str
    expected_action: AgentAction
    expected_tool_name: str | None = None
    observations: tuple[str, ...] = ()


@dataclass(frozen=True)
class DecisionEvalFailure:
    """Explain why one evaluation case failed."""

    case_name: str
    message: str


@dataclass(frozen=True)
class DecisionEvalReport:
    """Summarize deterministic decision evaluation results."""

    total: int
    passed: int
    failures: tuple[DecisionEvalFailure, ...]

    @property
    def accuracy(self) -> float:
        if self.total == 0:
            return 0.0

        return self.passed / self.total


def evaluate_decision_maker(
    decision_maker: DecisionMaker,
    cases: Iterable[DecisionEvalCase],
) -> DecisionEvalReport:
    """Measure action and tool selection across evaluation cases."""

    case_list = tuple(cases)
    failures: list[DecisionEvalFailure] = []

    for case in case_list:
        state = AgentState(goal=case.goal)
        for observation in case.observations:
            state.record_observation(observation)

        try:
            decision = decision_maker.decide(state)
        except Exception as error:
            failures.append(
                DecisionEvalFailure(
                    case_name=case.name,
                    message=(
                        "Decision maker raised "
                        f"{type(error).__name__}: {error}"
                    ),
                )
            )
            continue

        if decision.action is not case.expected_action:
            failures.append(
                DecisionEvalFailure(
                    case_name=case.name,
                    message=(
                        f"Expected action {case.expected_action.value}, "
                        f"received {decision.action.value}"
                    ),
                )
            )
            continue

        if (
            case.expected_tool_name is not None
            and decision.tool_name != case.expected_tool_name
        ):
            failures.append(
                DecisionEvalFailure(
                    case_name=case.name,
                    message=(
                        f"Expected tool {case.expected_tool_name}, "
                        f"received {decision.tool_name}"
                    ),
                )
            )

    return DecisionEvalReport(
        total=len(case_list),
        passed=len(case_list) - len(failures),
        failures=tuple(failures),
    )
