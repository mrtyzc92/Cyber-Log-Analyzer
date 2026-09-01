from dataclasses import dataclass, field
from enum import StrEnum


class AgentStatus(StrEnum):
    """Possible lifecycle states of an agent task."""

    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentState:
    """Store the mutable state of a single agent task."""

    goal: str
    status: AgentStatus = AgentStatus.READY
    current_step: int = 0
    max_steps: int = 5
    observations: list[str] = field(default_factory=list)
    result: str | None = None
    error: str | None = None

    def begin_step(self) -> None:
        """Mark the task as running and advance its step counter."""

        if self.current_step >= self.max_steps:
            message = "Agent step limit reached"
            self.status = AgentStatus.FAILED
            self.error = message
            raise RuntimeError(message)

        self.status = AgentStatus.RUNNING
        self.current_step += 1

    def record_observation(self, observation: str) -> None:
        """Record information returned by an agent tool."""

        self.observations.append(observation)

    def complete(self, result: str) -> None:
        """Mark the task as completed and store its final result."""

        self.status = AgentStatus.COMPLETED
        self.result = result
        self.error = None

    def fail(self, error: str) -> None:
        """Mark the task as failed and store its error."""

        self.status = AgentStatus.FAILED
        self.error = error
        self.result = None