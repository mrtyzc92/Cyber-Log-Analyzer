import pytest
from cyber_log_analyzer.agents.registry import ToolRegistry
from cyber_log_analyzer.agents.tools import AgentTool, ToolResult


class EchoTool(AgentTool):
    name = "echo"

    def run(self, tool_input: str) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            success=True,
            observation=tool_input,
        )


def test_tool_registry_registers_and_retrieves_tool():
    registry = ToolRegistry()
    tool = EchoTool()

    registry.register(tool)

    assert registry.get("echo") is tool

def test_tool_registry_rejects_unknown_tool():
    registry = ToolRegistry()

    with pytest.raises(KeyError, match="Tool not registered: missing"):
        registry.get("missing")

def test_tool_registry_rejects_duplicate_tool_name():
    registry = ToolRegistry()

    registry.register(EchoTool())

    with pytest.raises(ValueError, match="Tool already registered: echo"):
        registry.register(EchoTool())


def test_tool_registry_lists_registered_tool_names():
    registry = ToolRegistry()
    registry.register(EchoTool())

    assert registry.names == ("echo",)