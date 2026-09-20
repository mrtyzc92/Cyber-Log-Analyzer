from pathlib import Path

from cyber_log_analyzer.agents.decisions import AgentAction, AgentDecision
from cyber_log_analyzer.agents.log_analyzer_tool import LogAnalyzerTool
from cyber_log_analyzer.agents.loop import AgentLoop
from cyber_log_analyzer.agents.registry import ToolRegistry
from cyber_log_analyzer.agents.state import AgentState


class SecurityLogDecisionMaker:
    """Choose the fixed steps required for one security-log analysis."""

    def __init__(self, log_path: str | Path) -> None:
        self.log_path = str(log_path)

    def decide(self, state: AgentState) -> AgentDecision:
        if not state.observations:
            return AgentDecision(
                action=AgentAction.USE_TOOL,
                reason="The uploaded security log must be analyzed",
                tool_name=LogAnalyzerTool.name,
                tool_input=self.log_path,
            )

        return AgentDecision(
            action=AgentAction.COMPLETE,
            reason="The security-log analysis is complete",
        )


def run_security_log_agent(
    log_path: str | Path,
    threshold: int = 3,
) -> AgentState:
    """Run the security-log workflow through the guarded agent loop."""

    registry = ToolRegistry()
    registry.register(LogAnalyzerTool(threshold=threshold))

    loop = AgentLoop(
        registry=registry,
        decision_maker=SecurityLogDecisionMaker(log_path),
        max_steps=1,
    )

    return loop.run(goal="Analyze the uploaded security log")
