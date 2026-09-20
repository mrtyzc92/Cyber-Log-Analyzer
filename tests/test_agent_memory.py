import pytest

from cyber_log_analyzer.agents.memory import AgentMemory
from cyber_log_analyzer.agents.state import AgentState, AgentStatus


def test_agent_memory_records_terminal_state_snapshot():
    memory = AgentMemory(capacity=3)
    state = AgentState(goal="Analyze first log")
    state.complete("No suspicious activity")

    memory.remember(state)

    assert memory.recent() == (
        {
            "goal": "Analyze first log",
            "status": AgentStatus.COMPLETED,
            "outcome": "No suspicious activity",
        },
    )


def test_agent_memory_discards_oldest_entry_at_capacity():
    memory = AgentMemory(capacity=2)

    for number in range(3):
        state = AgentState(goal=f"Goal {number}")
        state.complete(f"Result {number}")
        memory.remember(state)

    assert [entry["goal"] for entry in memory.recent()] == [
        "Goal 1",
        "Goal 2",
    ]


def test_agent_memory_rejects_non_terminal_state():
    memory = AgentMemory()

    with pytest.raises(
        ValueError,
        match="Only terminal agent states can be remembered",
    ):
        memory.remember(AgentState(goal="Unfinished goal"))


def test_agent_memory_rejects_invalid_capacity():
    with pytest.raises(
        ValueError,
        match="Memory capacity must be greater than zero",
    ):
        AgentMemory(capacity=0)
