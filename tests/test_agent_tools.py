import pytest
from cyber_log_analyzer.agents.tools import AgentTool, ToolResult


def test_tool_result_represents_successful_observation():
    result = ToolResult(
        tool_name="log_analyzer",
        success=True,
        observation="3 suspicious IP addresses found",
    )

    assert result.tool_name == "log_analyzer"
    assert result.success is True
    assert result.observation == "3 suspicious IP addresses found"
    assert result.error is None

def test_tool_result_represents_failed_execution():
    result = ToolResult(
        tool_name="log_analyzer",
        success=False,
        observation="Log analysis could not be completed",
        error="Log file not found",
    )

    assert result.tool_name == "log_analyzer"
    assert result.success is False
    assert result.observation == "Log analysis could not be completed"
    assert result.error == "Log file not found"

def test_agent_tool_returns_structured_result():
    class EchoTool(AgentTool):
        name = "echo"

        def run(self, tool_input: str) -> ToolResult:
            return ToolResult(
                tool_name=self.name,
                success=True,
                observation=tool_input,
            )

    tool = EchoTool()
    result = tool.run("Log file validated")

    assert tool.name == "echo"
    assert result == ToolResult(
        tool_name="echo",
        success=True,
        observation="Log file validated",
    )

def test_agent_tool_cannot_be_created_without_run():
    class IncompleteTool(AgentTool):
        name = "incomplete"

    with pytest.raises(TypeError, match="abstract method.*run"):
        IncompleteTool()