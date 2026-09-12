from cyber_log_analyzer.agents.decisions import AgentAction, AgentDecision
from cyber_log_analyzer.agents.registry import ToolRegistry
from cyber_log_analyzer.agents.tools import AgentTool


class ToolSelector:
    """Resolve the tool requested by an agent decision."""

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def select(self, decision: AgentDecision) -> AgentTool:
        if decision.action is not AgentAction.USE_TOOL:
            raise ValueError(
                "Only USE_TOOL decisions can select a tool"
            )

        if decision.tool_name is None:
            raise ValueError(
                "Tool decision requires a tool name"
            )

        return self.registry.get(decision.tool_name)