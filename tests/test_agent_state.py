import pytest

from cyber_log_analyzer.agents.state import AgentState, AgentStatus


def test_agent_state_starts_ready():
    state = AgentState(goal="Analyze the security log")

    assert state.goal == "Analyze the security log"
    assert state.status is AgentStatus.READY
    assert state.current_step == 0
    assert state.max_steps == 5
    assert state.observations == []
    assert state.result is None
    assert state.error is None


def test_agent_state_begins_first_step():
    state = AgentState(goal="Analyze the security log")

    state.begin_step()

    assert state.status is AgentStatus.RUNNING
    assert state.current_step == 1

def test_agent_state_records_observation():
    state = AgentState(goal="Analyze the security log")

    state.record_observation("Log file validated")

    assert state.observations == ["Log file validated"]

def test_agent_state_rejects_step_above_limit():
    state = AgentState(
        goal="Analyze the security log",
        max_steps=1,
    )

    state.begin_step()

    with pytest.raises(RuntimeError, match="Agent step limit reached"):
        state.begin_step()

    assert state.current_step == 1
    assert state.status is AgentStatus.FAILED
    assert state.error == "Agent step limit reached"

def test_agent_state_completes_with_result():
         state = AgentState(goal="Analyze the security log")
         state.begin_step()

         state.complete("Security report created")

         assert state.status is AgentStatus.COMPLETED
         assert state.result == "Security report created"
         assert state.error is None

def test_agent_state_fails_with_error():
    state = AgentState(goal="Analyze the security log")
    state.begin_step()

    state.fail("Log file could not be analyzed")

    assert state.status is AgentStatus.FAILED
    assert state.error == "Log file could not be analyzed"
    assert state.result is None