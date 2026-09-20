from collections import deque

from cyber_log_analyzer.agents.state import AgentState, AgentStatus


MemoryEntry = dict[str, str | AgentStatus]


class AgentMemory:
    """Keep bounded snapshots of recently completed agent runs."""

    def __init__(self, capacity: int = 10) -> None:
        if capacity <= 0:
            raise ValueError("Memory capacity must be greater than zero")

        self._entries: deque[MemoryEntry] = deque(maxlen=capacity)

    def remember(self, state: AgentState) -> None:
        if state.status not in {
            AgentStatus.COMPLETED,
            AgentStatus.FAILED,
        }:
            raise ValueError(
                "Only terminal agent states can be remembered"
            )

        outcome = state.result if state.result is not None else state.error
        self._entries.append(
            {
                "goal": state.goal,
                "status": state.status,
                "outcome": outcome or "",
            }
        )

    def recent(self) -> tuple[MemoryEntry, ...]:
        """Return copies of stored entries from oldest to newest."""

        return tuple(dict(entry) for entry in self._entries)
