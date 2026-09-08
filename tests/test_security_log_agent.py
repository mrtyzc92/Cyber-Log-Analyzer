from cyber_log_analyzer.agents.security_log_agent import SecurityLogAgent
from cyber_log_analyzer.agents.state import AgentStatus
from cyber_log_analyzer.agents.tools import AgentTool, ToolResult
from cyber_log_analyzer.agents.log_analyzer_tool import LogAnalyzerTool


class SuccessfulTool(AgentTool):
    name = "successful_tool"

    def run(self, tool_input: str) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            success=True,
            observation="Security report created",
        )


def test_security_log_agent_completes_successful_task():
    agent = SecurityLogAgent(tool=SuccessfulTool())

    state = agent.run(
        goal="Analyze the security log",
        tool_input="security.log",
    )

    assert state.goal == "Analyze the security log"
    assert state.status is AgentStatus.COMPLETED
    assert state.current_step == 1
    assert state.observations == ["Security report created"]
    assert state.result == "Security report created"
    assert state.error is None

class FailedTool(AgentTool):
    name = "failed_tool"

    def run(self, tool_input: str) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            success=False,
            observation="Log analysis failed",
            error="Log file not found",
        )


def test_security_log_agent_fails_unsuccessful_task():
    agent = SecurityLogAgent(tool=FailedTool())

    state = agent.run(
        goal="Analyze the security log",
        tool_input="missing.log",
    )

    assert state.goal == "Analyze the security log"
    assert state.status is AgentStatus.FAILED
    assert state.current_step == 1
    assert state.observations == ["Log analysis failed"]
    assert state.result is None
    assert state.error == "Log file not found"

def test_security_log_agent_uses_real_log_analyzer_tool(tmp_path):
    log_file = tmp_path / "security.log"
    log_file.write_text(
        "\n".join(
            [
                "2026-08-18 09:12:42 | WARNING | "
                "192.168.1.25 | LOGIN_FAILED | admin",
                "2026-08-18 09:13:01 | WARNING | "
                "192.168.1.25 | LOGIN_FAILED | admin",
                "2026-08-18 09:13:19 | WARNING | "
                "192.168.1.25 | LOGIN_FAILED | admin",
            ]
        ),
        encoding="utf-8",
    )

    agent = SecurityLogAgent(
        tool=LogAnalyzerTool(threshold=3),
    )

    state = agent.run(
        goal="Analyze the security log",
        tool_input=str(log_file),
    )

    assert state.status is AgentStatus.COMPLETED
    assert state.current_step == 1
    assert len(state.observations) == 1
    assert "192.168.1.25" in state.observations[0]
    assert state.result is not None
    assert "192.168.1.25" in state.result
    assert state.error is None

def test_security_log_agent_records_real_tool_failure(tmp_path):
    missing_log_file = tmp_path / "missing.log"

    agent = SecurityLogAgent(
        tool=LogAnalyzerTool(threshold=3),
    )

    state = agent.run(
        goal="Analyze the security log",
        tool_input=str(missing_log_file),
    )

    assert state.status is AgentStatus.FAILED
    assert state.current_step == 1
    assert state.observations == ["Log analysis failed"]
    assert state.result is None
    assert state.error is not None
    assert "Log file not found" in state.error