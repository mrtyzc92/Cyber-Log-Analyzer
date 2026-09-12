from typing import Protocol

from cyber_log_analyzer.agents.decisions import AgentAction, AgentDecision
from cyber_log_analyzer.agents.registry import ToolRegistry
from cyber_log_analyzer.agents.state import AgentState
from cyber_log_analyzer.agents.tool_selector import ToolSelector


class DecisionMaker(Protocol):
    """Define the decision-making behavior required by the loop."""

    def decide(self, state: AgentState) -> AgentDecision:
        ...


class AgentLoop:
    """Run an agent until it reaches a final state."""

    def __init__(
        self,
        registry: ToolRegistry,
        decision_maker: DecisionMaker,
    ) -> None:
        self.decision_maker = decision_maker
        self.selector = ToolSelector(registry)

    def run(self, goal: str) -> AgentState:
        state = AgentState(goal=goal)

        while True:
            decision = self.decision_maker.decide(state)

            if decision.action is AgentAction.COMPLETE:
                result = (
                    state.observations[-1]
                    if state.observations
                    else decision.reason
                )
                state.complete(result)
                return state

            if decision.action is AgentAction.FAIL:
                state.fail(decision.reason)
                return state

            state.begin_step()

            tool = self.selector.select(decision)
            tool_result = tool.run(decision.tool_input or "")

            state.record_observation(tool_result.observation)

            if not tool_result.success:
                error = tool_result.error or tool_result.observation
                state.fail(error)
                return state