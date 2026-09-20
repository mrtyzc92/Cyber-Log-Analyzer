from cyber_log_analyzer.agents.tools import AgentTool


class ToolRegistry:
    """Store and retrieve the tools available to an agent."""

    def __init__(self) -> None:
        self._tools: dict[str, AgentTool] = {}

    def register(self, tool: AgentTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")

        self._tools[tool.name] = tool

    def get(self, tool_name: str) -> AgentTool:
        if tool_name not in self._tools:
            raise KeyError(f"Tool not registered: {tool_name}")

        return self._tools[tool_name]

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._tools)
