from cyber_log_analyzer.agents.decisions import AgentAction, AgentDecision
from cyber_log_analyzer.agents.loop import AgentLoop
from cyber_log_analyzer.agents.registry import ToolRegistry
from cyber_log_analyzer.agents.state import AgentState, AgentStatus
from cyber_log_analyzer.agents.tools import AgentTool, ToolResult


class CompleteImmediately:
    def decide(self, state: AgentState) -> AgentDecision:
        return AgentDecision(
            action=AgentAction.COMPLETE,
            reason="No additional work is required",
        )


def test_agent_loop_completes_from_decision():
    registry = ToolRegistry()
    decision_maker = CompleteImmediately()
    loop = AgentLoop(
        registry=registry,
        decision_maker=decision_maker,
    )

    state = loop.run(goal="Check the security log")

    assert state.status is AgentStatus.COMPLETED
    assert state.current_step == 0
    assert state.result == "No additional work is required"

class EchoTool(AgentTool):
    name = "echo"

    def run(self, tool_input: str) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            success=True,
            observation=tool_input,
        )


class UseToolThenComplete:
    def decide(self, state: AgentState) -> AgentDecision:
        if not state.observations:
            return AgentDecision(
                action=AgentAction.USE_TOOL,
                reason="The input must be processed",
                tool_name="echo",
                tool_input="Security log checked",
            )

        return AgentDecision(
            action=AgentAction.COMPLETE,
            reason="The required result was produced",
        )


def test_agent_loop_uses_tool_then_completes():
    registry = ToolRegistry()
    registry.register(EchoTool())

    loop = AgentLoop(
        registry=registry,
        decision_maker=UseToolThenComplete(),
    )

    state = loop.run(goal="Check the security log")

    assert state.status is AgentStatus.COMPLETED
    assert state.current_step == 1
    assert state.observations == ["Security log checked"]
    assert state.result == "Security log checked"

class FailImmediately:
    def decide(self, state: AgentState) -> AgentDecision:
        return AgentDecision(
            action=AgentAction.FAIL,
            reason="The task cannot be completed safely",
        )


def test_agent_loop_fails_from_decision():
    registry = ToolRegistry()

    loop = AgentLoop(
        registry=registry,
        decision_maker=FailImmediately(),
    )

    state = loop.run(goal="Check the security log")

    assert state.status is AgentStatus.FAILED
    assert state.current_step == 0
    assert state.observations == []
    assert state.result is None
    assert state.error == "The task cannot be completed safely"

class FailedTool(AgentTool):
    name = "failed_tool"

    def run(self, tool_input: str) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            success=False,
            observation="Log analysis failed",
            error="Log file not found",
        )


class UseFailedTool:
    def decide(self, state: AgentState) -> AgentDecision:
        return AgentDecision(
            action=AgentAction.USE_TOOL,
            reason="The log must be analyzed",
            tool_name="failed_tool",
            tool_input="missing.log",
        )


def test_agent_loop_stops_when_tool_fails():
    registry = ToolRegistry()
    registry.register(FailedTool())

    loop = AgentLoop(
        registry=registry,
        decision_maker=UseFailedTool(),
    )

    state = loop.run(goal="Check the security log")

    assert state.status is AgentStatus.FAILED
    assert state.current_step == 1
    assert state.observations == ["Log analysis failed"]
    assert state.result is None
    assert state.error == "Log file not found"

class AlwaysUseTool:
    def decide(self, state: AgentState) -> AgentDecision:
        return AgentDecision(
            action=AgentAction.USE_TOOL,
            reason="Continue using the tool",
            tool_name="echo",
            tool_input="Repeated observation",
        )


def test_agent_loop_stops_at_step_limit():
    registry = ToolRegistry()
    registry.register(EchoTool())

    loop = AgentLoop(
        registry=registry,
        decision_maker=AlwaysUseTool(),
        max_steps=2,
    )

    state = loop.run(goal="Keep checking the security log")

    assert state.status is AgentStatus.FAILED
    assert state.current_step == 2
    assert state.observations == [
        "Repeated observation",
        "Repeated observation",
    ]
    assert state.result is None
    assert state.error == "Agent step limit reached"