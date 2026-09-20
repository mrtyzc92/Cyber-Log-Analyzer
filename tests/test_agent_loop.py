import pytest
from cyber_log_analyzer.agents.decisions import AgentAction, AgentDecision
from cyber_log_analyzer.agents.loop import AgentLoop
from cyber_log_analyzer.agents.memory import AgentMemory
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

def test_agent_loop_rejects_invalid_step_limit():
    registry = ToolRegistry()

    with pytest.raises(
        ValueError,
        match="max_steps must be greater than zero",
    ):
        AgentLoop(
            registry=registry,
            decision_maker=CompleteImmediately(),
            max_steps=0,
        )

def test_agent_loop_rejects_empty_goal():
    registry = ToolRegistry()

    loop = AgentLoop(
        registry=registry,
        decision_maker=CompleteImmediately(),
    )

    with pytest.raises(
        ValueError,
        match="goal must not be empty",
    ):
        loop.run(goal="   ")


def test_agent_loop_remembers_completed_run():
    registry = ToolRegistry()
    memory = AgentMemory()
    loop = AgentLoop(
        registry=registry,
        decision_maker=CompleteImmediately(),
        memory=memory,
    )

    loop.run(goal="Check the security log")

    assert memory.recent()[0]["goal"] == "Check the security log"
    assert memory.recent()[0]["status"] is AgentStatus.COMPLETED


class SelectMissingTool:
    def decide(self, state: AgentState) -> AgentDecision:
        return AgentDecision(
            action=AgentAction.USE_TOOL,
            reason="Use a tool that is not registered",
            tool_name="missing_tool",
            tool_input="input",
        )


def test_agent_loop_fails_safely_for_unregistered_tool():
    loop = AgentLoop(
        registry=ToolRegistry(),
        decision_maker=SelectMissingTool(),
    )

    state = loop.run(goal="Check the security log")

    assert state.status is AgentStatus.FAILED
    assert state.current_step == 1
    assert state.error == (
        "Tool selection failed: Tool not registered: missing_tool"
    )


class CrashingTool(AgentTool):
    name = "crashing_tool"

    def run(self, tool_input: str) -> ToolResult:
        raise RuntimeError("tool process crashed")


class SelectCrashingTool:
    def decide(self, state: AgentState) -> AgentDecision:
        return AgentDecision(
            action=AgentAction.USE_TOOL,
            reason="Run the crashing tool",
            tool_name="crashing_tool",
            tool_input="input",
        )


def test_agent_loop_fails_safely_when_tool_raises_error():
    registry = ToolRegistry()
    registry.register(CrashingTool())
    loop = AgentLoop(
        registry=registry,
        decision_maker=SelectCrashingTool(),
    )

    state = loop.run(goal="Check the security log")

    assert state.status is AgentStatus.FAILED
    assert state.current_step == 1
    assert state.error == "Tool execution failed: tool process crashed"
