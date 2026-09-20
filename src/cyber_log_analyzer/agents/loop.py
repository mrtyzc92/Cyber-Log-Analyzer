from typing import Protocol

from cyber_log_analyzer.agents.decisions import AgentAction, AgentDecision
from cyber_log_analyzer.agents.memory import AgentMemory
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
        max_steps: int = 5,
        memory: AgentMemory | None = None,
    ) -> None:
        if max_steps <= 0:
            raise ValueError(
                "max_steps must be greater than zero"
            )

        self.decision_maker = decision_maker
        self.selector = ToolSelector(registry)
        self.max_steps = max_steps
        self.memory = memory

    def run(self, goal: str) -> AgentState:
        if not goal.strip():
            raise ValueError("goal must not be empty")

        state = AgentState(
            goal=goal,
            max_steps=self.max_steps,
        )

        while True:
            decision = self.decision_maker.decide(state)

            if decision.action is AgentAction.COMPLETE:
                result = (
                    state.observations[-1]
                    if state.observations
                    else decision.reason
                )
                state.complete(result)
                return self._finish(state)

            if decision.action is AgentAction.FAIL:
                state.fail(decision.reason)
                return self._finish(state)

            try:
                state.begin_step()
            except RuntimeError:
                return self._finish(state)

            try:
                tool = self.selector.select(decision)
            except (KeyError, ValueError) as error:
                message = (
                    error.args[0]
                    if isinstance(error, KeyError)
                    else str(error)
                )
                state.fail(f"Tool selection failed: {message}")
                return self._finish(state)

            try:
                tool_result = tool.run(decision.tool_input or "")
            except Exception as error:
                state.fail(f"Tool execution failed: {error}")
                return self._finish(state)

            state.record_observation(tool_result.observation)

            if not tool_result.success:
                error = tool_result.error or tool_result.observation
                state.fail(error)
                return self._finish(state)

    def _finish(self, state: AgentState) -> AgentState:
        if self.memory is not None:
            self.memory.remember(state)

        return state
