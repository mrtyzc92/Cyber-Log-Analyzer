import pytest
from cyber_log_analyzer.agents.decisions import AgentAction, AgentDecision
from cyber_log_analyzer.agents.registry import ToolRegistry
from cyber_log_analyzer.agents.tool_selector import ToolSelector
from cyber_log_analyzer.agents.tools import AgentTool, ToolResult


class EchoTool(AgentTool):
    name = "echo"

    def run(self, tool_input: str) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            success=True,
            observation=tool_input,
        )


def test_tool_selector_selects_tool_from_decision():
    registry = ToolRegistry()
    tool = EchoTool()
    registry.register(tool)
    selector = ToolSelector(registry)

    decision = AgentDecision(
        action=AgentAction.USE_TOOL,
        reason="Echo the supplied input",
        tool_name="echo",
        tool_input="hello",
    )

    assert selector.select(decision) is tool

def test_tool_selector_rejects_non_tool_decision():
    registry = ToolRegistry()
    selector = ToolSelector(registry)

    decision = AgentDecision(
        action=AgentAction.COMPLETE,
        reason="The task is already complete",
    )

    with pytest.raises(
        ValueError,
        match="Only USE_TOOL decisions can select a tool",
    ):
        selector.select(decision)

def test_tool_selector_requires_tool_name():
        registry = ToolRegistry()
        selector = ToolSelector(registry)

        decision = AgentDecision(
        action=AgentAction.USE_TOOL,
        reason="A tool must be used",
    )

        with pytest.raises(
        ValueError,
        match="Tool decision requires a tool name",
    ):
         selector.select(decision)