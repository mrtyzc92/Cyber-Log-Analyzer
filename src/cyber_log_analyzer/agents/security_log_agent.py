from cyber_log_analyzer.agents.state import AgentState
from cyber_log_analyzer.agents.tools import AgentTool


class SecurityLogAgent:
    """Coordinate an agent state with a security analysis tool."""

    def __init__(self, tool: AgentTool) -> None:
        self.tool = tool

    def run(self, goal: str, tool_input: str) -> AgentState:
        state = AgentState(goal=goal)

        state.begin_step()

        tool_result = self.tool.run(tool_input)
        state.record_observation(tool_result.observation)

        if tool_result.success:
            state.complete(tool_result.observation)
        else:
            error_message = tool_result.error or tool_result.observation
            state.fail(error_message)

        return state