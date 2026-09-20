from cyber_log_analyzer.agents.security_log_workflow import (
    run_security_log_agent,
)
from cyber_log_analyzer.agents.state import AgentStatus


def test_run_security_log_agent_completes_through_agent_loop(tmp_path):
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

    state = run_security_log_agent(log_file, threshold=3)

    assert state.status is AgentStatus.COMPLETED
    assert state.current_step == 1
    assert len(state.observations) == 1
    assert state.result is not None
    assert "192.168.1.25" in state.result


def test_run_security_log_agent_returns_structured_failure(tmp_path):
    malformed_log_file = tmp_path / "malformed.log"
    malformed_log_file.write_text("invalid log line", encoding="utf-8")

    state = run_security_log_agent(malformed_log_file, threshold=3)

    assert state.status is AgentStatus.FAILED
    assert state.current_step == 1
    assert state.observations == ["Log analysis failed"]
    assert state.error is not None
