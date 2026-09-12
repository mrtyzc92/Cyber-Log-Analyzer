from dataclasses import dataclass
from enum import StrEnum


class AgentAction(StrEnum):
    """Possible actions an agent can choose."""

    USE_TOOL = "use_tool"
    COMPLETE = "complete"
    FAIL = "fail"


@dataclass(frozen=True)
class AgentDecision:
    """Represent one decision made by an agent."""

    action: AgentAction
    reason: str
    tool_name: str | None = None
    tool_input: str | None = None